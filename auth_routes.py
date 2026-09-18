from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import get_session
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import LoginSchema, UsuarioSchema
from sqlalchemy.orm import Session 
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

auth_router = APIRouter(prefix="/auth", tags=['auth'])


def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)): 
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = { "sub": id_usuario, "exp": data_expiracao }
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado

def verificar_token(token, session):
    usuario = session.query(Usuario).filter(usuario.id==1)
    return usuario

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False

    return usuario

@auth_router.get("/")
async def autenticar(): 
    """
        Essa é a rota padrão de autenticação do sistema
    """
    return {"mensagem": "Você acessou a rota padrão de autenticação", "autenticado": False}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session = Depends(get_session)): 
    usuario = autenticar_usuario(usuario_schema.email, usuario_schema.senha, session)

    if usuario:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
    novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin)
    session.add(novo_usuario)
    session.commit()
    return { "mensagem": f"Usuário criado com sucesso {novo_usuario.email}" }

@auth_router.post("/login")
async def login(login_schema: LoginSchema,  session: Session = Depends(get_session)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    else: 
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, timedelta(days=7))

        return {
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "token_type": "Bearer"
        }

@auth_router.get("/refresh")
async def use_refresh_token(token, session: Session = Depends(get_session)): 
    usuario = verificar_token(token, session)
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token, 
        "token_type": "Bearer"
    }