from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import get_session
from main import bcrypt_context
from schemas import LoginSchema, UsuarioSchema
from sqlalchemy.orm import Session 

auth_router = APIRouter(prefix="/auth", tags=['auth'])


def criar_token(id_usuario): 
    token = f"fjsjdfksjfkf"
    return token

@auth_router.get("/")
async def autenticar(): 
    """
        Essa é a rota padrão de autenticação do sistema
    """
    return {"mensagem": "Você acessou a rota padrão de autenticação", "autenticado": False}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session = Depends(get_session)): 
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()

    if usuario:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
    novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin)
    session.add(novo_usuario)
    session.commit()
    return { "mensagem": f"Usuário criado com sucesso {novo_usuario.email}" }

@auth_router.post("/login")
async def login(login_schema: LoginSchema,  session: Session = Depends(get_session)):
    usuario = session.query(Usuario).filter(Usuario.email == login_schema.email).first()

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontra")
    else: 
        access_token = criar_token(usuario.id)
        return {"access_token": access_token, "token_type": "Bearer"}
    
