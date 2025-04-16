from fastapi import FastAPI, HTTPException
import logging
from main import sales_pipeline

app = FastAPI()
logger = logging.getLogger(__name__)

@app.post("/trigger_pipeline")
async def trigger_pipeline(mode: str = "batch", input_file: str = "sample_sales_data.csv", output_file: str = "cleaned_sales_data.csv"):
    try:
        if mode not in ["batch", "stream"]:
            raise HTTPException(status_code=400, detail="Invalid mode")
        logger.info(f"Received webhook trigger for mode={mode}, input={input_file}")
        sales_pipeline(mode=mode, input_file=input_file, output_file=output_file)
        return {"status": "Pipeline triggered successfully"}
    except Exception as e:
        logger.error(f"Webhook trigger failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)