import io
import json
import logging
from fdk import response

def handler(ctx, data: io.BytesIO = None):
    """
    Simplified test handler to verify basic function execution
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info("=== Function handler started ===")

    try:
        # Parse input
        body = json.loads(data.getvalue()) if data and data.getvalue() else {}
        logger.info(f"Received payload with keys: {list(body.keys())}")

        # Test importing the problematic libraries one by one
        import_results = {}

        try:
            import delta_sharing
            import_results['delta_sharing'] = 'OK'
            logger.info("delta_sharing imported successfully")
        except Exception as e:
            import_results['delta_sharing'] = f'FAILED: {str(e)}'
            logger.error(f"delta_sharing import failed: {e}")

        try:
            import pandas
            import_results['pandas'] = 'OK'
            logger.info("pandas imported successfully")
        except Exception as e:
            import_results['pandas'] = f'FAILED: {str(e)}'
            logger.error(f"pandas import failed: {e}")

        try:
            import oracledb
            import_results['oracledb'] = 'OK'
            logger.info("oracledb imported successfully")
        except Exception as e:
            import_results['oracledb'] = f'FAILED: {str(e)}'
            logger.error(f"oracledb import failed: {e}")

        try:
            import pyarrow
            import_results['pyarrow'] = 'OK'
            logger.info("pyarrow imported successfully")
        except Exception as e:
            import_results['pyarrow'] = f'FAILED: {str(e)}'
            logger.error(f"pyarrow import failed: {e}")

        result = {
            "status": "success",
            "message": "Function executed successfully",
            "import_results": import_results,
            "received_params": list(body.keys())
        }

        logger.info(f"Returning result: {result}")

        return response.Response(
            ctx,
            response_data=json.dumps(result),
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        logger.error(f"Error in handler: {str(e)}", exc_info=True)
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
