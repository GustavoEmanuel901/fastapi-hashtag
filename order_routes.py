from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session 
from dependencies import get_session
from schemas import PedidoSchema
from models import Pedido

order_router = APIRouter(prefix="/pedidos", tags=['pedidos'])

@order_router.get("/lista")
async def pedidos():
    """
        Essa é a rota padrão de pedidos do sistema
    """
    return {"mensagem": "Você acessou a rota de pedidos"}


@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(get_session)): 
    novo_pedido = Pedido(usuario=pedido_schema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": f"Pedido criado com sucesso. ID do Pedido: {novo_pedido.id}"}
