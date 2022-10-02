from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import FastAPI ,Depends , status , HTTPException, APIRouter, Body
from server.model.main import UnitBase, Unit, User, UnitCreate, UnitUpdate, PropositionBase, Proposition, PropositionCreate, Uservote, Propositioncomment, PropositioncommentCreate
from server.db import init_db, get_session
from server.auth.token import get_current_servicenumber, get_current_user

router = APIRouter()

@router.post("/{proposal_id}")
async def add_proposition_comment(proposal_id: int, prop: PropositioncommentCreate, session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
    # Check proposal writer's unit == commenter's unit
    query_proposal = select(Proposition).where(Proposition.proposal_id == proposal_id)
    exc_proposal = await session.execute(query_proposal)
    result_proposal = exc_proposal.scalars().one()
    proposal_writer = result_proposal.writer
    query_writer = select(User).where(User.service_number == proposal_writer)
    exc_writer = await session.execute(query_writer)
    result_writer = exc_writer.scalars().one()
    writer_unit = result_writer.unit_id
    commenter = await session.get(User, service_number)
    commenter_unit = commenter.unit_id
    if writer_unit != commenter_unit:
        raise HTTPException(
            status_code=404,
            detail="Logic_Error : Current user can't add comment to this proposal. Please contact Backend Developer !"
        )
    else:
        comment = Propositioncomment(commenter = service_number, proposal_id = proposal_id, contents = prop.contents)
        session.add(comment)
        await session.commit()
        await session.refresh(comment)

    return comment

@router.get("/{proposal_id}")
async def get_all_proposal_comment(proposal_id: int, session: AsyncSession = Depends(get_session)):
    result = []
    dp = {}
    query_comment = select(Propositioncomment).where(Propositioncomment.proposal_id == proposal_id)
    exc_comment = await session.execute(query_comment)
    result_query = exc_comment.scalars().all()
    if not result_query:
        raise HTTPException(
            status_code=404,
            detail="There is No exist comment in this proposal"
        )
    
    # mapping result
    for i in range(len(result_query)):
        service_number = result_query[i].commenter
        check_exist = service_number in dp
        if check_exist == False:
            commenter = await session.get(User, service_number)
            commenter_name = commenter.name
            dp[service_number] = commenter_name
            result.append(
                {
                    "commenter_service_number": service_number,
                    "commenter_name": commenter_name,
                    "contents": result_query[i].contents,
                    "proposal_id": result_query[i].proposal_id,
                    "comment_date": result_query[i].comment_date
                }
            )
        else:
            commenter_name = dp[service_number]
            result.append(
                {
                    "commenter_service_number": service_number,
                    "commenter_name": commenter_name,
                    "contents": result_query[i].contents,
                    "proposal_id": result_query[i].proposal_id,
                    "comment_date": result_query[i].comment_date
                }
            )

    return result