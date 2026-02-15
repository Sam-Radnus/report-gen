FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.14

# System dependencies required by reportlab
RUN dnf install -y \
    freetype \
    libjpeg-turbo \
    fontconfig \
    dejavu-sans-fonts \
    && dnf clean all

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Lambda code
COPY lambda_function.py .

CMD ["lambda_function.lambda_handler"]
