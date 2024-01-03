from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

app = FastAPI()

# Crea el cliente de S3
s3 = boto3.client('s3')
bucket_name = "clbb-3d-objects"  # Nombre bucket S3

@app.get("/modelos")
def listar_modelos_3d():
    try:
        # Obtener la lista de objetos en el bucket S3
        response = s3.list_objects_v2(Bucket=bucket_name)

        # Extraer los nombres de los modelos
        modelos = [obj['Key'] for obj in response.get('Contents', [])]
        
        # Devolver la lista de nombres de modelos
        return {"modelos": modelos}

    except NoCredentialsError:
        return {"error": "Credenciales no disponibles"}
    except ClientError as e:
        # Manejo de errores específicos de ClientError
        return {"error": str(e)}
    except Exception as e:
        # Manejo de cualquier otro error
        return {"error": str(e)}

@app.get("/modelos/{nombre_modelo}")
async def obtener_modelo_3d(nombre_modelo: str):
    try:
        # Intenta obtener el objeto del bucket S3
        response = s3.get_object(Bucket=bucket_name, Key=nombre_modelo)
        
        # Crea una respuesta de streaming
        return StreamingResponse(response['Body'], media_type="application/octet-stream")

    except NoCredentialsError:
        return {"error": "Credenciales no disponibles"}
    except ClientError as e:
        # Manejo de errores específicos de S3 (por ejemplo, el archivo no se encuentra)
        if e.response['Error']['Code'] == "NoSuchKey":
            return {"error": "El modelo no existe"}
        else:
            return {"error": str(e)}
    except Exception as e:
        # Manejo de cualquier otro error
        return {"error": str(e)}
