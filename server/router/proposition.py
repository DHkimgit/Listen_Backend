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

@router.post("/")
async def add_proposition(prop: PropositionCreate, session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
    proposal = Proposition(writer = service_number, title = prop.title, contents = prop.contents)
    unit_id_query = await session.execute(select(User.unit_id).where(User.service_number == service_number))
    unit_id = unit_id_query.scalars().one()
    unit =  await session.get(Unit, unit_id)
    current_proposition_total = unit.proposition_total
    setattr(unit, 'proposition_total', current_proposition_total + 1)
    session.add(unit)
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
    result = prop.scalars().all()
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Wrong service number"
        )
    return result

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
    votestatus_query = select(Votestatus.name).where(Votestatus.id == proposal.vote_status)
    exc_votestatus = await session.execute(votestatus_query)
    result_votestatus = exc_votestatus.scalars().one()
    status_query = select(Propositionstatus.name).where(Propositionstatus.id == proposal.status)
    exc_status = await session.execute(status_query)
    result_status = exc_status.scalars().one()
    result = {
        "title" : proposal.title,
        "writer" : proposal.writer,
        "unit_name" : writer_unit_name,
        "vote_favor" : proposal.vote_favor,
        "vote_against" : proposal.vote_against,
        "vote_status": result_votestatus,
        "frst_reg_date" : proposal.frst_reg_date,
        "last_chg_date" : proposal.last_chg_date,
        "status" : result_status,
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

@router.patch("/contents/{proposal_id}")
async def update_proposition_contents(prop: PropositionUpdate, proposal_id: int, session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
    proposal = await session.get(Proposition, proposal_id)
    if proposal.writer != service_number:
        raise HTTPException(
            status_code=404,
            detail="Current user can't update this proposition"
        )
    current_time = datetime.now(KST)
    setattr(proposal, 'contents', prop.contents)
    setattr(proposal, 'last_chg_date', current_time)
    session.add(proposal)
    await session.commit()
    await session.refresh(proposal)
    return proposal

# 건의문삭제. 댓글 까지 전부 삭제됨
@router.delete("/{proposal_id}")
async def delete_proposal(proposal_id: int, session: AsyncSession = Depends(get_session), service_number: str = Depends(get_current_user)):
    proposal = await session.get(Proposition, proposal_id)
    unit_id_query = await session.execute(select(User.unit_id).where(User.service_number == service_number))
    unit_id = unit_id_query.scalars().one()
    unit =  await session.get(Unit, unit_id)
    current_proposition_total = unit.proposition_total
    setattr(unit, 'proposition_total', current_proposition_total - 1)
    session.add(unit)
    await session.commit()
    if not proposal:
        raise HTTPException(status_code=404)
    
    if proposal.status != 1:
        raise HTTPException(
            status_code=404,
            detail="Can't delete! check status"
        )
    query_comment = select(Propositioncomment).where(Propositioncomment.proposal_id == proposal_id)
    exe_comment = await session.execute(query_comment)
    result = exe_comment.scalars().all()
    for i in range(len(result)):
        await session.delete(result[i])
        await session.commit()
    await session.delete(proposal)
    await session.commit()
    return {"ok"}

@router.get("/units/{unit_id}")
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
                }
            )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="proposition doesn't exist"
        )

    return result

@router.get("/date/test")
async def test_date(session: AsyncSession = Depends(get_session)):
    proposal = await session.get(Proposition, 1)
    query = select(Proposition.frst_reg_date)
    exc = await session.execute(query)
    result = exc.scalars().all()
    KSTs = timedelta(hours=+9)
    kijun = timedelta(days = 1)
    current_time = datetime.now()
    result = current_time - result[0] + KSTs
    if result >= kijun:
        print("하루 넘음")
    else:
        print("안넘음")
    print(str(result))
    return str(result)

@router.get("/proposalstatus/date/test")
async def check_proposal_status(session: AsyncSession = Depends(get_session)):
    query = select(Proposition).where(Proposition.status == 1)
    exc = await session.execute(query)
    result = exc.scalars().all()
    roop_len = len(result)
    kst_correction = timedelta(hours=+9)
    time_criteria = timedelta(days = 1)
    current_time = datetime.now()
    for i in range(roop_len):
        write_time = result[i].frst_reg_date
        check_timeout = current_time - write_time + kst_correction
        if check_timeout >= time_criteria:
            proposal_id = result[i].proposal_id
            db_prop = await session.get(Proposition, proposal_id)
            setattr(db_prop ,'status', 2)
            session.add(db_prop)
            await session.commit()
        else:
            pass
    return "finish"