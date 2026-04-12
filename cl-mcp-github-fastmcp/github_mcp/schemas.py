from pydantic import BaseModel, Field


class GitHubTokenData(BaseModel):
    token: str = Field(..., description="The GitHub access token.")
    scopes: list[str] = Field(
        default=[],
        description="The scopes granted to the token. Example: ['repo', 'read:org'], etc.",
    )
