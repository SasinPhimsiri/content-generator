"""Main entry point for Jenosize Content Generator."""

import asyncio
import sys
import socket
from pathlib import Path
import argparse
from loguru import logger

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config import config
from src.core.ollama_client import ollama_client


def find_free_port(start_port: int, max_attempts: int = 10) -> int:
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except socket.error:
            continue
    raise RuntimeError(f"Could not find free port starting from {start_port}")


async def check_dependencies():
    """Check if all dependencies are available."""
    logger.info("Checking system dependencies...")
    
    # Check Ollama availability
    try:
        model_available = await ollama_client.check_model_availability()
        if not model_available:
            logger.warning(f"Model {ollama_client.model} not available")
            logger.info("Attempting to pull model...")
            pull_success = await ollama_client.pull_model()
            if not pull_success:
                logger.error("Failed to pull model. Please ensure Ollama is running and try again.")
                return False
        logger.info("Ollama model available")
    except Exception as e:
        logger.error(f"Ollama not available: {e}")
        logger.error("Please ensure Ollama is installed and running:")
        logger.error("1. Install Ollama from https://ollama.ai")
        logger.error("2. Run: ollama serve")
        logger.error("3. Pull model: ollama pull qwen3:4b-instruct-2507-q4_K_M")
        return False
    
    logger.info("All dependencies checked")
    return True


def run_api():
    """Run the FastAPI backend server."""
    import uvicorn
    from src.api.main import app
    
    # Find a free port starting from the configured port
    try:
        api_port = find_free_port(config.api.port)
        logger.info(f"Starting FastAPI backend server on port {api_port}...")
        uvicorn.run(
            app,
            host=config.api.host,
            port=api_port,
            workers=1,
            log_level="info"
        )
    except RuntimeError as e:
        logger.error(f"Could not start API server: {e}")
        raise


def run_frontend():
    """Run the Gradio frontend."""
    from src.frontend.gradio_app import ContentGeneratorUI
    
    # Find a free port starting from 7860
    try:
        frontend_port = find_free_port(7860)
        logger.info(f"Starting Gradio frontend on port {frontend_port}...")
        app = ContentGeneratorUI()
        app.launch(
            server_name="0.0.0.0",
            server_port=frontend_port,
            share=False
        )
    except RuntimeError as e:
        logger.error(f"Could not start frontend: {e}")
        raise


async def run_full_system():
    """Run both API and frontend."""
    import multiprocessing
    import time
    
    logger.info("Starting full Jenosize Content Generator system...")
    
    # Check dependencies first
    if not await check_dependencies():
        return
    
    # Find free ports and display info
    try:
        api_port = find_free_port(config.api.port)
        frontend_port = find_free_port(7860)
        
        logger.info(f"System will start on:")
        logger.info(f"   - API: http://localhost:{api_port}")
        logger.info(f"   - Frontend: http://localhost:{frontend_port}")
        logger.info(f"   - API Docs: http://localhost:{api_port}/docs")
        
    except RuntimeError as e:
        logger.error(f"Could not find free ports: {e}")
        return
    
    # Start API server in separate process
    api_process = multiprocessing.Process(target=run_api)
    api_process.start()
    
    # Wait a bit for API to start
    logger.info("Waiting for API server to start...")
    time.sleep(5)
    
    try:
        # Start frontend in main process
        run_frontend()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        # Clean up API process
        api_process.terminate()
        api_process.join()


async def run_style_learning():
    """Run the automated style learning system."""
    logger.info("Running automated style learning...")
    
    try:
        from src.auto_style_learner import AutomatedStyleLearner
        learner = AutomatedStyleLearner()
        count = await learner.run_full_automation(max_articles=10, force_refresh=False)
        if count > 0:
            logger.info(f"Successfully updated style learning with {count} articles")
        else:
            logger.warning("No new content was added to style learning")
    except Exception as e:
        logger.error(f"Style learning failed: {e}")


async def test_generation():
    """Test content generation with a sample request."""
    logger.info("Testing content generation...")
    
    if not await check_dependencies():
        return
    
    from src.agents.coordinator import content_coordinator
    from src.core.data_pipeline import data_processor
    
    # Sample request
    test_request = {
        "topic": "Digital Transformation in Healthcare",
        "category": "Digital Transformation",
        "industry": "Healthcare",
        "target_audience": "healthcare executives",
        "seo_keywords": ["digital transformation", "healthcare", "technology"],
        "content_length": "medium"
    }
    
    try:
        # Process input
        processed_input = await data_processor.process_input(test_request)
        
        # Generate content
        result = await content_coordinator.generate_content(processed_input)
        
        logger.info("Content generation test successful!")
        logger.info(f"Generated content length: {len(result['final_content'])} characters")
        logger.info(f"Quality score: {result['quality_score']:.1f}/10")
        
        # Save test output
        test_output_file = Path("test_output.txt")
        with open(test_output_file, "w", encoding="utf-8") as f:
            f.write("# Test Content Generation Output\n\n")
            f.write(f"**Topic:** {test_request['topic']}\n")
            f.write(f"**Quality Score:** {result['quality_score']:.1f}/10\n\n")
            f.write("## Generated Content\n\n")
            f.write(result['final_content'])
        
        logger.info(f"Test output saved to: {test_output_file}")
        
    except Exception as e:
        logger.error(f"Content generation test failed: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Jenosize Content Generator")
    parser.add_argument(
        "mode",
        choices=["api", "frontend", "full", "test", "check", "style"],
        help="Run mode: api (backend only), frontend (UI only), full (both), test (generation test), check (dependencies), style (update style learning)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    logger.info(f"Starting Jenosize Content Generator in {args.mode} mode")
    
    if args.mode == "api":
        run_api()
    elif args.mode == "frontend":
        run_frontend()
    elif args.mode == "full":
        asyncio.run(run_full_system())
    elif args.mode == "test":
        asyncio.run(test_generation())
    elif args.mode == "check":
        asyncio.run(check_dependencies())
    elif args.mode == "style":
        asyncio.run(run_style_learning())


if __name__ == "__main__":
    main()
