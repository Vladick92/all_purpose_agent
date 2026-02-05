import time

def stream_text(responce):
    for word in responce:
        if word:
            yield word 
            time.sleep(0.015)

def get_image_path(history):
    photo_path=None
    if history:
        for content in history:
            for part in content.parts:
                if part.function_response:
                    tool_data=part.function_response.response
                    photo_path=tool_data.get('result',{}).get('photo_path')
    return photo_path

AVAILABLE_TEXT_MODELS={
    'gemini 2.5 flash lite': 'gemini-2.5-flash-lite',
    'gemini 2.5 flash': 'gemini-2.5-flash',
    'gemini 2.5 flash pro': 'gemini-2.5-flash-pro',
    'gemini 3 flash': 'gemini-3-flash-preview',
    'gemini 3 pro': 'gemini-3-pro-preview',
}

AVAILABLE_IMAGE_MODELS={
    'imagen 4 fast generate': 'imagen-4.0-fast-generate-001',
    'imagen 4 generate': 'imagen-4.0-generate-001',
    'imagen 4 ultra generate': 'imagen-4.0-ultra-generate-001',
}

