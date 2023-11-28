import random

from fastapi import HTTPException
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlmodel import select

from src.config.database import get_session
from src.models.reservas_model import Reserva
from src.models.voos_model import Voo

reservas_router = APIRouter(prefix="/reservas")


@reservas_router.get("/{id_voo}")
def lista_reservas_voo(id_voo: int):
    with get_session() as session:
        statement = select(Reserva).where(Reserva.voo_id == id_voo)
        reservas = session.exec(statement).all()
        return reservas@reservas_router.post("")
def cria_reserva(reserva: Reserva):
    with get_session() as session:
        existing_reserva = session.exec(
            select(Reserva).where(Reserva.documento == reserva.documento)
        ).first()

        if existing_reserva:
            raise HTTPException(
                status_code=400,
                detail="Já existe uma reserva com este número de documento =\.",
            )

        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                content={"message": f"Voo com id {reserva.voo_id} não encontrado."},
                status_code=404,
            )

        # TODO - Validar se existe uma reserva para o mesmo documento

        codigo_reserva = "".join(
            [str(random.randint(0, 999)).zfill(3) for _ in range(2)]
        )

        reserva.codigo_reserva = codigo_reserva
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva


def faz_checkin(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
        statement = select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)
        reserva = session.exec(statement).first()

        if not reserva:
            raise HTTPException(
                status_code=404,
                detail=f"Reserva com o código {codigo_reserva} não existe"
            )

        statement = select(Voo).where(Voo.id == reserva.voo_id)
        voo = session.exec(statement).first()

        if not voo:
            raise HTTPException(
                status_code=404,
                detail=f"Voo com o ID {reserva.voo_id} não encontrado."
            )

        poltrona_atual = getattr(voo, f"poltrona_{num_poltrona}")

        if poltrona_atual is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Essa poltrona {num_poltrona} já está ocupada."
            )

        setattr(voo, f"poltrona_{num_poltrona}", codigo_reserva)

        session.add(voo)
        session.commit()
        session.refresh(voo)

        return {"message": f"Check-in realizado, Código: {codigo_reserva} na poltrona: {num_poltrona}."}


@reservas_router.post("/{codigo_reserva}/troca-poltrona/{novo_num_poltrona}")
def troca_poltrona(codigo_reserva: str, novo_num_poltrona: int):
    with get_session() as session:
        reserva = session.exec(
            select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)
        ).first()

        if not reserva:
            return JSONResponse(
                content={"message": f"Reserva com código {codigo_reserva} não encontrada."},
                status_code=404,
            )

        if reserva.status != "checkin":
            return JSONResponse(
                content={"message": f"Reserva não realizou o check-in."},
                status_code=400,
            )

        reserva.num_poltrona = novo_num_poltrona

        session.commit()
        session.refresh(reserva)
        return reserva
    

@reservas_router.patch("/{codigo_reserva}/checkin/{num_poltrona}")
def checkin_patch(codigo_reserva: str, num_poltrona: int, session: Session = Depends(get_session)):
    try:
        reserva = session.execute(select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)).scalar()
        if not reserva:
            raise HTTPException(
                status_code=404,
                detail=f"Reserva com o código {codigo_reserva} não encontrada."
            )

        voo = session.execute(select(Voo).where(Voo.id == reserva.voo_id)).scalar()
        if not voo:
            raise HTTPException(
                status_code=404,
                detail=f"Voo com o ID {reserva.voo_id} não encontrado."
            )

        poltrona_atual = getattr(voo, f"poltrona_{num_poltrona}")
        if poltrona_atual is not None:
            raise HTTPException(
                status_code=403,
                detail=f"Poltrona {num_poltrona} já ocupada."
            )

        setattr(voo, f"poltrona_{num_poltrona}", codigo_reserva)

        session.commit()

        return {"message": f"Check-in realizado com sucesso para a reserva {codigo_reserva} na poltrona {num_poltrona}."}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro inesperado: {str(e)}"
        )

