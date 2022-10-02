from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import FastAPI ,Depends , status , HTTPException, APIRouter, Body
from server.model.main import UnitBase, Unit, UnitCreate, UnitUpdate, PropositionBase, Proposition, PropositionCreate, Uservote, Propositioncomment, User
from server.db import init_db, get_session
from server.auth.token import get_current_servicenumber, get_current_user

router = APIRouter()


@router.post("/")
async def add_proposition(prop: PropositionCreate, session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
    proposal = Proposition(writer = service_number, title = prop.title, contents = prop.contents, status = prop.status)
    session.add(proposal)
    await session.commit()
    await session.refresh(proposal)
    return proposal

@router.get("/me")
async def get_active_user_proposition(session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
    query = select(Proposition).where(Proposition.writer == service_number)
    prop = await session.execute(query)
    if prop == None:
        raise HTTPException(status_code=404)
    result = prop.scalars().all()
    return result

@router.get("/{service_number}")
async def get_proposition(service_number: str, session: AsyncSession = Depends(get_session)):
    query = select(Proposition).where(Proposition.writer == service_number)
    prop = await session.execute(query)
    if prop == None:
        raise HTTPException(status_code=404)
    result = prop.scalars().all()
    return result

@router.patch("/vote/{proposal_id}")
async def vote_proposition(proposal_id: int, session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
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
    current_number_of_vote = db_prop.number_of_vote
    setattr(db_prop ,'number_of_vote', current_number_of_vote + 1)
    vote = Uservote(proposal_id = proposal_id, voter = service_number)
    session.add(db_prop)
    session.add(vote)
    await session.commit()
    await session.refresh(db_prop)
    await session.refresh(vote)
    return db_prop

@router.get("/withcomment/{proposal_id}")
async def get_proposition_and_comment(proposal_id: int, session: AsyncSession = Depends(get_session)):
    proposal = await session.get(Proposition, proposal_id)
    print(proposal)
    writer_unit = await session.execute(select(User.unit_id).where(User.service_number == proposal.writer))
    writer_unit_id = writer_unit.scalars().one()
    exc_unit_name = await session.execute(select(Unit.name).where(Unit.id == writer_unit_id))
    writer_unit_name = exc_unit_name.scalars().one()
    print(writer_unit_name)
    query_comment = select(Propositioncomment).where(Proposition.proposal_id == proposal_id, Propositioncomment.proposal_id == proposal_id)
    exc_comment = await session.execute(query_comment)
    result_comment = exc_comment.scalars().all()

    result = {
        "title" : proposal.title,
        "writer" : proposal.writer,
        "unit_name" : writer_unit_name,
        "number_of_vote" : proposal.number_of_vote,
        "vote_status": proposal.vote_status,
        "frst_reg_date" : proposal.frst_reg_date,
        "last_chg_date" : proposal.last_chg_date,
        "status" : proposal.status,
        "comments": []
    }
    dp = {}
    for i in range(len(result_comment)):
        service_number = result_comment[i].commenter
        check_exist = service_number in dp
        if check_exist == False:
            commenter = await session.get(User, service_number)
            commenter_name = commenter.name
            dp[service_number] = commenter_name
            comment = {
                "commenter_service_number": service_number,
                "commenter_name": commenter_name,
                "content": result_comment[i].contents,
                "comment_date": result_comment[i].comment_date
            }
            result["comments"].append(comment)
        else:
            commenter_name = dp[service_number]
            comment = {
                "commenter_service_number": service_number,
                "commenter_name": commenter_name,
                "content": result_comment[i].contents,
                "comment_date": result_comment[i].comment_date
            }
            result["comments"].append(comment)
    
    return result
