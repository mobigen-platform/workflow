import json
from typing import List, Optional, Any

from pydantic import BaseModel, Field, model_validator, field_validator


# DAG 데이터 모델 정의
class UDFInputSchema(BaseModel):
    name: str = Field(..., description="input Name")
    type: str = Field(..., description="input Type")
    required: bool = Field(..., description="필수/옵션")
    default_value: Optional[str] = Field(..., description="input default value")
    description: Optional[str] = Field(..., description="input 설명")


class UDFOutputSchema(BaseModel):
    name: str = Field(..., description="output Name")
    type: str = Field(..., description="output Type")
    description: Optional[str] = Field(..., description="output 설명")


class UDFUploadRequest(BaseModel):
    function_name: str = Field("run", description="main function name (default: run)")
    operator_type: str = Field("python", description="operator type [python, python_virtual, docker]")
    docker_image: Optional[str] = Field(..., description="docker image name")

    inputs: List[UDFInputSchema]
    output: UDFOutputSchema

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value: Any) -> Any:
        print(f"validate_to_json : {value}")
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    @field_validator("docker_image", mode='before')
    def check_docker_image_required(cls, v, validation_info):
        print(f"check_docker_image_required : {v}, {validation_info}")
        if validation_info.data.get("operator_type") == "docker" and not v:
            raise ValueError("docker_image is required when operator_type is 'docker'")
        return v
