import base64
import requests
from os import path
from pprint import pprint

from typing import Annotated
from models.dropbox_meta_models import UpdateDropboxSignConfigRequest
from models.dropbox_models import SignerInfo
# from pydantic import EmailStr

from fastapi import APIRouter, HTTPException, UploadFile, Depends, Response, Body, status, File, Request, Form
from pydantic import BaseModel
from fastapi.responses import JSONResponse

import logging
from config import settings
import json
# from auth.jwt_auth import get_private_key, get_jwt_token

from dropbox_sign import ApiClient, ApiException, Configuration, apis, models, EventCallbackRequest, EventCallbackHelper, ApiException

class WebHookInfo(BaseModel):
  event: dict

# Configure logging
logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.post("/update-config")
async def update_dropbox_sign_config(config: UpdateDropboxSignConfigRequest):
    try:
        # Update the .env file
        env_content = f"DB_API_KEY={config.api_key}\n"
        with open(".env", "w") as env_file:
            env_file.write(env_content)

        return JSONResponse(status_code=200, content={"status":"OK"})

    except Exception as e:
        # Log the error appropriately
        print(f"Error updating Dropbox Sign configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the Dropbox Sign configuration.",
        )


@router.post("/send-test-signature-request")
async def send_test_envelope(
    signer_info: SignerInfo = Body(...),
    # access_token: str = Cookie(None),  # Read the token from an HTTP-only cookie
):  
    try:
        configuration = Configuration(
            username=settings.db_api_key,
        )

        with ApiClient(configuration) as api_client:
            signature_request_api = apis.SignatureRequestApi(api_client)

            # Read the demo document
            demo_docs_path = path.join(settings.demo_docs_path, "World_Wide_Corp_lorem.pdf")
            with open(demo_docs_path, "rb") as file:
                doc_pdf_bytes = file.read()

            signer = models.SubSignatureRequestSigner(
                email_address=signer_info.signer_email,
                name=signer_info.signer_name,
                order=0,
            )

            data = models.SignatureRequestSendRequest(
                title="Test Envelope",
                subject="Please sign this document",
                message="This is a test document. Please sign it.",
                signers=[signer],
                files=[open(path.join(settings.demo_docs_path, "World_Wide_Corp_lorem.pdf"), "rb")],
                test_mode=True,
            )

            response = signature_request_api.signature_request_send(data)
            return response
        
    except ApiException as e:
        return ("Exception when calling Dropbox Sign API: %s\n" % e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-template")
async def create_template_embed_url(
    template_name: str = Body(...),
    base_document: UploadFile = File(...),
):
    try:
        file_content = await base_document.read()

        configuration = Configuration(
            username=settings.db_api_key,
        )

        with ApiClient(configuration) as api_client:
            template_api = apis.TemplateApi(api_client)

            role_1 = models.SubTemplateRole(
                name="Client",
                order=0,
            )

            role_2 = models.SubTemplateRole(
                name="Witness",
                order=1,
            )

            merge_field_1 = models.SubMergeField(
                name="Full Name",
                type="text",
            )

            merge_field_2 = models.SubMergeField(
                name="Is Registered?",
                type="checkbox",
            )

            field_options = models.SubFieldOptions(
                date_format="DD - MM - YYYY",
            )

            data = models.TemplateCreateEmbeddedDraftRequest(
                client_id="2ecad39961dd373ec1957cf7f7d36240",
                files=[open("./app/static/demo_documents/World_Wide_Corp_lorem.pdf", "rb")],
                title="Test Template",
                subject="Please sign this document",
                message="For your approval",
                signer_roles=[role_1, role_2],
                cc_roles=["Manager"],
                merge_fields=[merge_field_1, merge_field_2],
                field_options=field_options,
                test_mode=True,
            )

            response = template_api.template_create_embedded_draft(data)
            return response

    except ApiException as e:
        error_body = e.body if hasattr(e, "body") else str(e)
        raise HTTPException(status_code=500, detail=f"Dropbox Sign API error: {error_body}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.post("/webhook")
async def dropbox_sign_webhook(request: Request):
    try:
        # Read the multipart form-data request body
        form_data = await request.form()
        json_data = json.loads(form_data.get("json"))  # Extract the 'json' field

        if not json_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'json' field in webhook payload.",
            )

        # Verify and parse the webhook event using Dropbox Sign's SDK helper
        try:
            event = EventCallbackRequest.init(json_data)
        except ApiException as e:
            logging.error(f"Error verifying webhook event: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or unverified webhook event.",
            )

        # Log the event type
        event_type = EventCallbackHelper.get_callback_type(event)
        logging.info(f"Received Dropbox Sign event: {event_type}")

        # Respond to acknowledge the webhook
        return {"status": "success", "message": f"Event {event_type} logged successfully."}

    except Exception as e:
        logging.error(f"Error handling webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the webhook.",
        )
