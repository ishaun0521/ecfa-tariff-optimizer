import io
import pandas as pd
from fastapi import UploadFile

async def parse_uploaded_file(file: UploadFile):
    content = await file.read()
    name = file.filename.lower()
    if name.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(content))
    elif name.endswith('.xlsx') or name.endswith('.xls'):
        df = pd.read_excel(io.BytesIO(content))
    else:
        raise ValueError('Only CSV/XLSX/XLS files are supported')

    return {
        "filename": file.filename,
        "columns": list(df.columns),
        "row_count": int(len(df)),
        "preview": df.head(5).fillna('').to_dict(orient='records')
    }
