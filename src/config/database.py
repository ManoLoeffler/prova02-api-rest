from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine

# CONFIGURAÇÕES DA CONEXAO COM O BANCO DE DADOS
PG_USERNAME = "root"
PG_PASSWORD = "postgres"
PG_HOST = "localhost"
PG_PORT = 54323
PG_DATABASE = "airline_db"

# CONFIGURAÇÃO CONEXÃO
connect_args = {}

# MONTANDO A URL DE CONEXÃO
# postgresql://root:postgres@localhost:54321/oficina
db_url = f"postgresql://{PG_USERNAME}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"

# CRIA A CONEXÃO COM O BANCO (ENGINE)
engine = create_engine(db_url, echo=True, connect_args=connect_args)


# METODO QUE CRIA TODAS AS TABELAS NO BANCO
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# RETORNA A INSTANCIA DA CONEXAO
def get_engine():
    return engine

# OBTEM UMA SESSAO DO BANCO
@contextmanager
def get_session():
    yield Session(engine)
