import io
import json
import logging
from fdk import response

def handler(ctx, data: io.BytesIO = None):
    """
    Simple test handler to verify function basics work
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info("Function started successfully")

    try:
        body = json.loads(data.getvalue()) if data and data.getvalue() else {}
        logger.info(f"Received payload: {body}")

        result = {
            "status": "success",
            "message": "Function is working!",
            "received_keys": list(body.keys())
        }

        return response.Response(
            ctx,
            response_data=json.dumps(result),
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return response.Response(
            ctx,
            response_data=json.dumps({
                "status": "error",
                "error": str(e),
                "type": type(e).__name__
            }),
            headers={"Content-Type": "application/json"},
            status_code=500
        )
