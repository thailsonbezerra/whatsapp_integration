import os
from urllib.parse import urlparse
from typing import Optional

def infer_mime_type_from_url(url: str) -> str:
    """
    Inferir o mime-type de uma URL com base na extensão do arquivo.
    """
    # Mapeamento de extensões para mime-types
    mime_types = {
        # Audio
        ".aac": "audio/aac",
        ".amr": "audio/amr",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        
        # Documentos
        ".txt": "text/plain",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".pdf": "application/pdf",
        
        # Imagens
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg", 
        ".png": "image/png",

        # Vídeos
        ".3gp": "video/3gpp",
        ".mp4": "video/mp4",
    }
    
    # Extrai o caminho do arquivo da URL
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # Extrai a extensão
    extension = os.path.splitext(path)[1].lower()
    
    return mime_types.get(extension)


def get_meta_media_type(mime_type: str) -> Optional[str]:
    """
    Maps standard MIME types to Meta's media type categories.
    Returns one of: 'image', 'video', 'audio', 'document', 'sticker' or None
    """
    if not mime_type:
        return None
        
    if mime_type.startswith("image/"):
        return "sticker" if mime_type == "image/webp" else "image"
    elif mime_type.startswith("video/"):
        return "video"
    elif mime_type.startswith("audio/"):
        return "audio"
    elif mime_type in [
        "application/pdf",
        "application/msword",
        "application/vnd.ms-excel",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain"
    ]:
        return "document"
    
    return None