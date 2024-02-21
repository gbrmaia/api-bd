from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pydantic import BaseModel

# Criação da aplicação FastAPI
app = FastAPI()

# Configuração do banco de dados SQLite
DATABASE_URL = "sqlite:///./banco_oficial.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definição do modelo para os dados
class Dados(Base):
    __tablename__ = "dados"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    endereco = Column(String)
    data_nascimento = Column(String)
    telefone = Column(String, unique=True, index=True)

# Criação das tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Pydantic model para validação de dados de entrada
class DadosInput(BaseModel):
    nome: str
    endereco: str
    data_nascimento: str
    telefone: str

class DadosUpdate(BaseModel):
    nome: str = None
    endereco: str = None
    data_nascimento: str = None
    telefone: str = None

# Função para adicionar valor ao banco de dados
@app.post("/add_value/")
async def add_value(dados: DadosInput):
    db = SessionLocal()

    # Verificar se o telefone já existe no banco de dados
    if db.query(Dados).filter(Dados.telefone == dados.telefone).first():
        return {"messagecadastro": "japossuicadastro"}

    # Adicionar os dados ao banco de dados
    db_dados = Dados(**dados.dict())
    db.add(db_dados)
    db.commit()
    db.refresh(db_dados)

    return {"messagecadastro": "cadastrado"}

# Endpoint para obter os dados associados ao número de telefone
@app.get("/get_data/{telefone}")
def get_data_by_telefone(telefone: str):
    db = SessionLocal()

    # Procurar o número de telefone no banco de dados
    resultado = db.query(Dados).filter(Dados.telefone == telefone).first()

    if not resultado:
        return {"dados_associados": "notfoundnumber"}

    # Retornar os dados associados ao número de telefone
    dados_associados = {"nome": resultado.nome, "endereco": resultado.endereco, "data_nascimento": resultado.data_nascimento, "telefone": resultado.telefone}
    return {"dados_associados": dados_associados}

@app.get("/verificar_cadastro/{telefone}")
def verificar_cadastro(telefone: str):
    db = SessionLocal()

    # Verificar se o número de telefone existe no banco de dados
    resultado = db.query(Dados).filter(Dados.telefone == telefone).first()

    if resultado:
        dados_associados = {"nome": resultado.nome, "endereco": resultado.endereco, "data_nascimento": resultado.data_nascimento, "telefone": resultado.telefone}
        return { "nome": resultado.nome, "endereco": resultado.endereco, "data_nascimento": resultado.data_nascimento, "telefone": resultado.telefone }
    else:
        return {"confirmcadastro": "naopossuicadastro"}


@app.delete("/limpar_info/{telefone}")
def limpar_info(telefone: str):
    db = SessionLocal()
    
    resultado = db.query(Dados).filter(Dados.telefone == telefone).first()
    
    if not resultado:
        return {"limparcadastro": "não encotramos o número"}
    
    db.delete(resultado)
    db.commit()
    
    return {"limparcadastro": "cadastro limpo"}

@app.get("/listar_dados/")
def listar_dados():
    db = SessionLocal()

    # Consultar todos os dados no banco de dados
    dados = db.query(Dados).all()

    # Criar uma lista para armazenar os resultados
    lista_dados = []

    # Iterar sobre os resultados e adicionar ao formato desejado
    for item in dados:
        lista_dados.append({
            "nome": item.nome,
            "endereco": item.endereco,
            "data_nascimento": item.data_nascimento,
            "telefone": item.telefone
        })

    return {"dados": lista_dados}

@app.put("/update_data/{telefone}")
def update_data(telefone: str, dados_update: DadosUpdate):
    db = SessionLocal()

    # Procurar o número de telefone no banco de dados
    db_dados = db.query(Dados).filter(Dados.telefone == telefone).first()

    if not db_dados:
        raise HTTPException(status_code=404, detail="Número de telefone não encontrado")

    # Atualizar informações conforme necessário
    for field, value in dados_update.dict(exclude_unset=True).items():
        setattr(db_dados, field, value)

    db.commit()
    db.refresh(db_dados)

    return {"message": f"Informações atualizadas com sucesso para {db_dados.nome}."}



    