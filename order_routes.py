from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from dependencies import get_session, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema
from models import Pedido, Usuario, ItemPedido

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

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(get_session), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido: 
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin or usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer esse modificação")
    pedido.status = "CANCELADO"
    session.commit()
    return { 
        "mensagem": f"Pedido Número: {pedido.id} cancelado com sucesso",
        "pedido": pedido
    }

@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(get_session), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
    else: 
        pedidos = session.query(Pedido).all()
        return {
            "pedidos": pedidos
        }

@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, 
                                item_pedido_schema: ItemPedidoSchema, 
                                session: Session = Depends(get_session), 
                                usuario: Usuario = Depends(verificar_token)):

    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()

    if not pedido: 
        raise HTTPException(status_code=400, detail="Pedido não existente")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")

    item_pedido = ItemPedido(item_pedido_schema.quantidade, 
                             item_pedido_schema.sabor, 
                             item_pedido_schema.tamanho, 
                             item_pedido_schema.preco_unitario,
                             id_pedido)

    pedido.calcular_preco()
    session.add(item_pedido)
    session.commit()
    return {
        "mensagem": "Item adicionado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }