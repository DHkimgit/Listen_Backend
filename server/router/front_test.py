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

@router.post("/units/{unit_id}/proposals")
async def post_proposition_by_unit_id(prop: PropositionCreate, unit_id: int, session: AsyncSession = Depends(get_session)):
    service_number: str = Depends(get_current_user)

@router.get("/units/{unit_id}/proposals/simple")
async def get_proposition_by_unit_id_simple_result(unit_id: int, session: AsyncSession = Depends(get_session)):
    service_number_list = []
    result = []
    unit = await session.get(Unit, unit_id)
    if not unit:
        raise HTTPException(
            status_code=404,
            detail="unit doesn't exist"
        )
    query_user = select(User.service_number).where(User.unit_id == unit_id)
    exc_user = await session.execute(query_user)
    result_user = exc_user.scalars().all()
    for k in range(len(result_user)):
        service_number_list.append(result_user[k])
    for i in range(len(service_number_list)):
        current_service_number = service_number_list[i]
        query_proposal = select(Proposition).where(Proposition.writer == current_service_number)
        exc_proposal = await session.execute(query_proposal)
        result_proposal = exc_proposal.scalars().all()
        for j in range(len(result_proposal)):
            result.append(
                {
                    "title": result_proposal[j].title,
                    "contents": result_proposal[j].contents,
                }
            )
    return result

@router.get("/units/{unit_id}/proposals")
async def get_proposition_by_unit_id(unit_id: int, session: AsyncSession = Depends(get_session)):
    service_number_list = []
    result = []
    unit = await session.get(Unit, unit_id)
    if not unit:
        raise HTTPException(
            status_code=404,
            detail="unit doesn't exist"
        )
    query_user = select(User.service_number).where(User.unit_id == unit_id)
    exc_user = await session.execute(query_user)
    result_user = exc_user.scalars().all()

    for k in range(len(result_user)):
        service_number_list.append(result_user[k])

    for i in range(len(service_number_list)):
        current_service_number = service_number_list[i]
        query_user = select(User).where(User.service_number == current_service_number)
        exc_user = await session.execute(query_user)
        result_user = exc_user.scalars().all()
        query_proposal = select(Proposition).where(Proposition.writer == current_service_number)
        exc_proposal = await session.execute(query_proposal)
        result_proposal = exc_proposal.scalars().all()
        dp = {}
        for j in range(len(result_proposal)):
            query_status = select(Propositionstatus).where(Propositionstatus.id == result_proposal[j].status)
            exc_status = await session.execute(query_status)
            result_status = exc_status.scalars().all()
            query_votestatus = select(Votestatus).where(Votestatus.id == result_proposal[j].vote_status)
            exc_votestatus = await session.execute(query_votestatus)
            result_votestatus = exc_votestatus.scalars().all()
            query_answerstatus = select(Answerstatus).where(Answerstatus.id == result_proposal[j].answer_status)
            exc_answerstatus = await session.execute(query_answerstatus)
            result_answerstatus = exc_answerstatus.scalars().all()
            query_comment = select(Propositioncomment).where(Proposition.proposal_id == result_proposal[j].proposal_id, Propositioncomment.proposal_id == result_proposal[j].proposal_id)
            exc_comment = await session.execute(query_comment)
            result_comment = exc_comment.scalars().all()
            comments = []
            for l in range(len(result_comment)):
                service_number = result_comment[l].commenter
                check_exist = service_number in dp
                if check_exist == False:
                    commenter = await session.get(User, service_number)
                    commenter_name = commenter.name
                    dp[service_number] = commenter_name
                    comment = {
                        "commenter_service_number": service_number,
                        "commenter_name": commenter_name,
                        "content": result_comment[l].contents,
                        "comment_date": result_comment[l].comment_date
                    }
                    comments.append(comment)
                else:
                    commenter_name = dp[service_number]
                    comment = {
                        "commenter_service_number": service_number,
                        "commenter_name": commenter_name,
                        "content": result_comment[l].contents,
                        "comment_date": result_comment[l].comment_date
                    }
                    comments.append(comment)
            result.append(
                {
                    "writer_servicenumber": result_proposal[j].writer,
                    "writer_name": result_user[0].name,
                    "writer_rank": result_user[0].rank,
                    "title": result_proposal[j].title,
                    "contents": result_proposal[j].contents,
                    "frst_reg_date": result_proposal[j].frst_reg_date,
                    "last_chg_date": result_proposal[j].last_chg_date,
                    "vote_favor": result_proposal[j].vote_favor,
                    "vote_against": result_proposal[j].vote_against,
                    "status": result_status[0].name,
                    "vote_status": result_votestatus[0].name,
                    "answer_status": result_answerstatus[0].name,
                    "comments": comments
                }
            )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="proposition doesn't exist"
        )

    return result
