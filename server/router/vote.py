from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import FastAPI ,Depends , status , HTTPException, APIRouter, Body
from server.model.main import UnitBase, Unit, UnitCreate, UnitUpdate, PropositionBase, Propositionstatus, Votestatus, PropositionUpdate, Proposition, PropositionCreate, Uservote, Propositioncomment, User, Propositionstorage, Answerstatus
from server.db import init_db, get_session
from server.auth.token import get_current_servicenumber, get_current_user
from datetime import datetime, timedelta
import pytz

KST = pytz.timezone('Asia/Seoul')

router = APIRouter()

async def check_current_vote_standard(proposal_id: int, service_number: str, current_vote_favor: int, session: AsyncSession = Depends(get_session)):
    query_user = await session.execute(select(User).where(User.service_number == service_number))
    user = query_user.scalars().one()
    unit_id = user.unit_id
    unit = await session.get(Unit, unit_id)
    proposal = await session.get(Proposition, proposal_id)
    member = unit.member
    standard = int(member/2) + 1
    trending_standard = int(standard/2)

    # status == 3 은 이미 건의문의 상태가 Trending 이므로 투표 종료 기준의 절반을 도달한 상태임
    if proposal.status == 3:
        # 득표수가 투표 종료 기준을 도달하는지 확인
        if current_vote_favor >= standard:
            setattr(proposal, 'vote_status', 2)
            setattr(proposal, 'answer_status', 2)
            setattr(proposal, 'status', 4)
            session.add(proposal)
            await session.commit()
            return 2
        else:
            return 0
    
    else:
        if current_vote_favor >= trending_standard:
            # 투표 종료 기준선의 절반 도달 => status Trending 으로 변경
            setattr(proposal, 'status', 3)
            session.add(proposal)
            await session.commit()
            return 1
        else:
            # 아무것도 안바뀜
            return 0


async def send_proposals_to_unit_admin(proposal_id: int, service_number: str, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, service_number)
    unit_id = user.unit_id
    admin_query = await session.execute(select(User).where(User.authority == '간부', User.unit_id == unit_id))
    admins = admin_query.scalars().all()
    for i in range(len(admins)):
        storage = Propositionstorage(user = admins[i].service_number, proposal_id = proposal_id, unit_id = unit_id)
        session.add(storage)
        await session.commit()
        await session.refresh(storage)
    
    return True

@router.get("/votestatus/{proposal_id}")
async def vote_status(proposal_id: int, session: AsyncSession = Depends(get_session)):
    result = []
    proposal = await session.get(Proposition, proposal_id)
    vote_favor = proposal.vote_favor
    vote_against = proposal.vote_against
    result.append(vote_favor)
    result.append(vote_against)
    return result  

@router.patch("/votefavor/{proposal_id}")
async def vote_proposition_favor(proposal_id: int, session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
    # check duplicate vote
    query = select(Uservote).where(Uservote.voter == service_number, Uservote.proposal_id == proposal_id)
    result = await session.execute(query)
    check = result.scalars().all()
    if check:
        raise HTTPException(
            status_code=404,
            detail="Current user already vote this proposition"
        )
    # Increase the number of votes and add vote data
    db_prop = await session.get(Proposition, proposal_id)
    current_number_of_vote_favor = db_prop.vote_favor
    setattr(db_prop ,'vote_favor', current_number_of_vote_favor + 1)
    vote = Uservote(proposal_id = proposal_id, voter = service_number, vote_type = 1)
    session.add(db_prop)
    session.add(vote)
    await session.commit()
    await session.refresh(db_prop)
    await session.refresh(vote)
    member = await check_current_vote_standard(proposal_id, service_number, current_number_of_vote_favor + 1, session)
    if member == 2:
        send_proposal_to_admin = await send_proposals_to_unit_admin(proposal_id, service_number, session)
    print(member)
    return db_prop

@router.patch("/voteagainst/{proposal_id}")
async def vote_proposition_against(proposal_id: int, session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
    # check duplicate vote
    query = select(Uservote).where(Uservote.voter == service_number, Uservote.proposal_id == proposal_id)
    result = await session.execute(query)
    check = result.scalars().all()
    if check:
        raise HTTPException(
            status_code=404,
            detail="Current user already vote this proposition"
        )
    # Increase the number of votes and add vote data
    db_prop = await session.get(Proposition, proposal_id)
    current_number_of_vote_against = db_prop.vote_against
    setattr(db_prop ,'vote_against', current_number_of_vote_against + 1)
    vote = Uservote(proposal_id = proposal_id, voter = service_number, vote_type = 2)
    session.add(db_prop)
    session.add(vote)
    await session.commit()
    await session.refresh(db_prop)
    await session.refresh(vote)
    return db_prop