from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from app.db.main import engine #, init_db
from app.books.routes import router as book_router
from app.auth.routes import router as auth_router
from app.reviews.routes import review_router
from app.db.redis import init_redis, close_redis
#we don't need this init_db function here anymore since we are using alembic for migrations

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("------------server before starting----------")
    # await  init_db()
    await init_redis()

    yield

    print("------just before shutting down-------")
    await close_redis()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

# Add CORS middleware - Add this section
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development)
    # For production, use specific origins like:
    # allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(book_router, prefix="/books")
app.include_router(auth_router, prefix="/auth")
app.include_router(review_router, prefix="/reviews")


@app.get("/", status_code = status.HTTP_200_OK)
def root():
    return {"message": "welcome to my server"}
