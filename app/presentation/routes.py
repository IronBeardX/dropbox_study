import base64
from os import path
from pprint import pprint

from typing import Annotated
# from pydantic import EmailStr

from fastapi import APIRouter, HTTPException, UploadFile, Depends


from app.config import settings
# from app.auth.jwt_auth import get_private_key, get_jwt_token

from dropbox_sign import ApiClient, ApiException, Configuration, apis, models

router = APIRouter()

@router.get("/get-account-info")
async def account_info():
    configuration = Configuration(
        # Configure HTTP basic authorization: api_key
        username=settings.db_api_key,
        # or, configure Bearer (JWT) authorization: oauth2
        # access_token="YOUR_ACCESS_TOKEN",
    )

    with ApiClient(configuration) as api_client:
        account_api = apis.AccountApi(api_client)

        try:
            response = account_api.account_get(email_address="alejandroyeroval@gmail.com")
            return response
        except ApiException as e:
            return("Exception when calling Dropbox Sign API: %s\n" % e)
        
@router.get("/send-sign-request")
async def sign_request():
    configuration = Configuration(
        # Configure HTTP basic authorization: api_key
        username=settings.db_api_key,
        # or, configure Bearer (JWT) authorization: oauth2
        # access_token="YOUR_ACCESS_TOKEN",
    )

    with ApiClient(configuration) as api_client:
        signature_request_api = apis.SignatureRequestApi(api_client)

        signer_1 = models.SubSignatureRequestSigner(
            email_address="alejandroyeroval@gmail.com",
            name="Jack",
            order=0,
        )

        signer_2 = models.SubSignatureRequestSigner(
            email_address="alejandroyeroval@gmail.com",
            name="Jill",
            order=1,
        )

        signing_options = models.SubSigningOptions(
            draw=True,
            type=True,
            upload=True,
            phone=True,
            default_type="draw",
        )

        field_options = models.SubFieldOptions(
            date_format="DD - MM - YYYY",
        )

        data = models.SignatureRequestSendRequest(
            title="NDA with Acme Co.",
            subject="The NDA we talked about",
            message="Please sign this NDA and then we can discuss more. Let me know if you have any questions.",
            signers=[signer_1, signer_2],
            cc_email_addresses=[
                "lawyer1@dropboxsign.com",
                "lawyer2@dropboxsign.com",
            ],
            files=[open("./app/static/demo_documents/World_Wide_Corp_lorem.pdf", "rb")],
            metadata={
                "custom_id": 1234,
                "custom_text": "NDA #9",
            },
            signing_options=signing_options,
            field_options=field_options,
            test_mode=True,
        )

        try:
            response = signature_request_api.signature_request_send(data)
            return response
        except ApiException as e:
            return ("Exception when calling Dropbox Sign API: %s\n" % e)

@router.get("/check-sign-request")
async def check_request(signature_request_id: str):
    configuration = Configuration(
        # Configure HTTP basic authorization: api_key
        username=settings.db_api_key,
        # or, configure Bearer (JWT) authorization: oauth2
        # access_token="YOUR_ACCESS_TOKEN",
    )

    with ApiClient(configuration) as api_client:
        signature_request_api = apis.SignatureRequestApi(api_client)

        # signature_request_id = "ded674c9c0a786aff8fd0d548bf993aaef1949d6"

        try:
            response = signature_request_api.signature_request_get(signature_request_id)
            return response
        except ApiException as e:
            return ("Exception when calling Dropbox Sign API: %s\n" % e)