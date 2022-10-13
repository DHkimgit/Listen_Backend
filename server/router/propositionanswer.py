from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import FastAPI ,Depends , status , HTTPException, APIRouter, Body
from server.model.main import UnitBase, Unit, User, UnitCreate, UnitUpdate, PropositionBase, Proposition, PropositionCreate, Uservote, Propositioncomment, PropositioncommentCreate, PropositionanswerCreate, Propositionanswer
from server.db import init_db, get_session
from server.auth.token import get_current_servicenumber, get_current_user

router = APIRouter()

@router.post("/{proposal_id}")
async def add_proposition_answer(prop: PropositionanswerCreate, proposal_id: int, session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
    proposal = await session.get(Proposition, proposal_id)
    proposal_writer = proposal.writer
    query_writer = select(User).where(User.service_number == proposal_writer)
    exc_writer = await session.execute(query_writer)
    result_writer = exc_writer.scalars().one()
    writer_unit = result_writer.unit_id
    answerer = await session.get(User, service_number)
    answerer_unit = answerer.unit_id

    if writer_unit != answerer_unit:
        raise HTTPException(
            status_code=404,
            detail="Logic_Error : Current user can't add answer to this proposal. Please contact Backend Developer !"
        )
    else:
        answer = Propositionanswer(proposal_id = proposal_id, writer = service_number, title = prop.title, contents = prop.contents)
        session.add(answer)
        setattr(proposal, "answer_status", 4)
        session.add(proposal)
        await session.commit()
        await session.refresh(answer)
    
    return answer

@router.get("/{proposal_id}")
async def get_proposal_answer(proposal_id: int, session: AsyncSession = Depends(get_session)):
    query = select(Propositionanswer).where(Propositionanswer.proposal_id == proposal_id)
    exc_proposal = await session.execute(query)
    result = exc_proposal.scalars().all()
    return result