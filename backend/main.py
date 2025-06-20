from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import predict, compare, insights
from utils.constants import TICKER_LIST
from utils.features import get_features_for_ticker
from utils.sentiment import get_sentiment_for_ticker
from pydantic import BaseModel
from typing import List
import logging
import os
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompareRequest(BaseModel):
    tickers: List[str]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    try:
        logger.info("🚀 StAI API starting up...")
        
        # Log environment info
        logger.info(f"Working directory: {Path.cwd()}")
        logger.info(f"Main file location: {Path(__file__).resolve()}")
        
        # Check critical directories
        project_root = Path.cwd()
        models_dir = project_root / "models"
        utils_dir = project_root / "utils"
        
        logger.info(f"Project root: {project_root}")
        logger.info(f"Models directory exists: {models_dir.exists()}")
        logger.info(f"Utils directory exists: {utils_dir.exists()}")
        
        if models_dir.exists():
            try:
                model_files = list(models_dir.glob("*.pkl"))
                logger.info(f"Found {len(model_files)} model files")
            except Exception as e:
                logger.error(f"Error reading models directory: {e}")
        
        logger.info("✅ StAI API startup complete")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
    
    yield
    
    # Cleanup
    logger.info("🔄 StAI API shutting down...")
    logger.info("✅ StAI API shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="StAI - Stock Prediction API",
    description="Advanced Stock Price Prediction with Machine Learning",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:3001",
        "http://localhost:5173",
        "https://st-ai.vercel.app",
        "https://*.railway.app",  # Railway domains
        "https://*.up.railway.app"  # Railway legacy domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url.path),
            "timestamp": datetime.now().isoformat()
        }
    )

# Include routers
app.include_router(predict.router)
app.include_router(compare.compare_router)
app.include_router(insights.insights_router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    try:
        # Get some basic stats
        project_root = Path.cwd()
        models_dir = project_root / "models"
        
        model_count = 0
        if models_dir.exists():
            try:
                model_files = list(models_dir.glob("*.pkl"))
                model_count = len(model_files)
            except:
                pass
        
        return {
            "message": "StAI - Stock Prediction made easy",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "supported_tickers": len(TICKER_LIST),
            "available_models": model_count,
            "endpoints": {
                "predict": "/predict/{symbol}",
                "compare": "/compare/",
                "insights": "/insights/{symbol}",
                "tickers": "/tickers",
                "features": "/features/{ticker}",
                "sentiment": "/sentiment/{ticker}",
                "health": "/health"
            }
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        return {
            "message": "StAI - Stock Prediction made easy",
            "status": "running with warnings",
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway and monitoring"""
    try:
        project_root = Path.cwd()
        models_dir = project_root / "models"
        utils_dir = project_root / "utils"
        
        # Check critical components
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "checks": {
                "models_directory": models_dir.exists(),
                "utils_directory": utils_dir.exists(),
                "ticker_list": len(TICKER_LIST) > 0,
            }
        }
        
        # Count available models
        if models_dir.exists():
            try:
                model_files = list(models_dir.glob("*.pkl"))
                health_status["checks"]["available_models"] = len(model_files)
            except Exception as e:
                health_status["checks"]["model_check_error"] = str(e)
        
        # Determine overall health
        critical_checks = ["models_directory", "utils_directory", "ticker_list"]
        if all(health_status["checks"].get(check, False) for check in critical_checks):
            health_status["status"] = "healthy"
        else:
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/tickers")
def get_supported_tickers():
    """Get list of supported stock tickers"""
    try:
        return {
            "tickers": TICKER_LIST,
            "count": len(TICKER_LIST),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting tickers: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving tickers: {str(e)}")

@app.get("/features/{ticker}")
def get_features(ticker: str):
    """Get technical features for a specific ticker"""
    try:
        features = get_features_for_ticker(ticker.upper())
        if features is None:
            raise HTTPException(status_code=404, detail=f"Feature data not found for ticker: {ticker}")
        
        return {
            "ticker": ticker.upper(),
            "features": features,
            "count": len(features) if isinstance(features, list) else 0,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting features for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving features: {str(e)}")

@app.get("/sentiment/{ticker}")
def get_sentiment(ticker: str):
    """Get sentiment analysis for a specific ticker"""
    try:
        result = get_sentiment_for_ticker(ticker.upper())
        
        if not result or not result.get('articles'):
            raise HTTPException(status_code=404, detail=f"No news found for ticker: {ticker}")
        
        # Add metadata
        result["timestamp"] = datetime.now().isoformat()
        result["ticker"] = ticker.upper()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sentiment for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving sentiment: {str(e)}")

@app.get("/debug/info")
async def debug_info():
    """Debug endpoint for deployment troubleshooting"""
    try:
        project_root = Path.cwd()
        
        # Get directory structure
        structure = {}
        try:
            for item in project_root.iterdir():
                if item.is_dir():
                    structure[item.name] = "directory"
                else:
                    structure[item.name] = "file"
        except Exception as e:
            structure["error"] = str(e)
        
        # Check models directory
        models_info = {}
        models_dir = project_root / "models"
        if models_dir.exists():
            try:
                model_files = [f.name for f in models_dir.glob("*.pkl")]
                models_info["files"] = model_files[:10]  # Limit output
                models_info["total_count"] = len(list(models_dir.glob("*.pkl")))
            except Exception as e:
                models_info["error"] = str(e)
        else:
            models_info["status"] = "directory_not_found"
        
        return {
            "working_directory": str(project_root),
            "main_file": str(Path(__file__).resolve()),
            "directory_structure": structure,
            "models_info": models_info,
            "environment": {
                "PORT": os.getenv("PORT", "Not set"),
                "PYTHONPATH": os.getenv("PYTHONPATH", "Not set"),
                "PWD": os.getenv("PWD", "Not set")
            },
            "ticker_list_length": len(TICKER_LIST),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Railway deployment entry point
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"🚀 Starting StAI API on port {port}")
    logger.info(f"📁 Working directory: {Path.cwd()}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )