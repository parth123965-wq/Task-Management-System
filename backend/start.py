# run.py or inside if __name__ == "__main__":
import uvicorn

if __name__ == "__main__":
    try:
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\nServer stopped cleanly.")