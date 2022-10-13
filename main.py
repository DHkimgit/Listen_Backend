# uvicorn main:app --reload --host=0.0.0.0 --port=${PORT:-8000}
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from server.router.user import router as UserRouter
from server.router.unit import router as UnitRouter
from server.router.login import router as LoginRouter
from server.router.proposition import router as PropositionRouter
from server.router.propositioncomment import router as PropositionCommentRouter
from server.router.propositionanswer import router as PropositionAnswerRouter
from server.router.front_test import router as FronttestRouter
from server.router.vote import router as VoteRouter
from server.model.main import Proposition
from fastapi_utils.tasks import repeat_every
from server.db import init_db, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import pytz

app = FastAPI()

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UserRouter, tags=["User"], prefix="/user")
app.include_router(UnitRouter, tags=["Unit"], prefix="/unit")
app.include_router(LoginRouter, tags=["Login"], prefix="/login")
app.include_router(PropositionRouter, tags=["Proposition"], prefix="/proposition")
app.include_router(PropositionCommentRouter, tags=["PropositionComment"], prefix="/proposition/comment")
app.include_router(PropositionAnswerRouter, tags=["PropositionAnswer"], prefix="/proposition/answer")
app.include_router(FronttestRouter, tags=["FronttestRouter"])
app.include_router(VoteRouter, tags=["VoteRouter"])

#건의문이 게시되고 일정 시간이 지날경우 status를 new에서 normal 로 바꿔주는 함수를 주기마다 반복적으로 실행합니다.
@app.on_event("startup")
@repeat_every(seconds=60 * 300)
def check_proposal_status(session: AsyncSession = Depends(get_session)):
    query = select(Proposition).where(Proposition.status == 1)
    exc = session.execute(query)
    result = exc.scalars().all()
    roop_len = len(result)
    kst_correction = timedelta(hours=+9)
    time_criteria = timedelta(days = 1)
    current_time = datetime.now()
    for i in range(roop_len):
        write_time = result[i].frst_reg_date
        check_timeout = current_time - write_time + kst_correction
        print("!!!")
        if check_timeout >= time_criteria:
            proposal_id = result[i].proposal_id
            db_prop = session.get(Proposition, proposal_id)
            setattr(db_prop ,'status', 2)
            session.add(db_prop)
            session.commit()
        else:
            pass
    return "finish"

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}