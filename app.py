import os
import shutil
import gradio as gr
import requests
# from dotenv import load_dotenv
from openai import OpenAI

# load_dotenv()

upstage_api_key = os.environ.get("UPSTAGE_API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not upstage_api_key:
    raise ValueError("UPSTAGE api key가 없습니다")
if not openai_api_key:
    raise ValueError("OpenAI api key가 없습니다")

input_dir = "./docs/input"
parsed_dir = "./docs/parsed"
os.makedirs(input_dir, exist_ok=True)
os.makedirs(parsed_dir, exist_ok=True)

url = "https://api.upstage.ai/v1/document-digitization"
headers = {"Authorization": f"Bearer {upstage_api_key}"}

client = OpenAI(api_key=openai_api_key)

# 기본 프롬프트 템플릿
DEFAULT_PROMPT = """문서를 다음 형식에 따라 요약하세요.

## 요약 형식    
1. 문서 정보
- 제목 :
- 저자 :
- 작성 날짜 :
- 작성 기관 :

2. 전체 요약 :

3. 세부 요약 :


## 요약 방법
1. 문서의 제목과 저자, 작성 날짜 및 기관을 확인하여 "1. 문서 정보"에 적으세요. 정보를 찾을 수 없다면 빈칸으로 두세요.
2. 문서의 전체 구조를 파악하세요.
3. 파악한 구조별로 핵심 내용을 2-3문장으로 추출하세요.
4. 추출한 핵심 내용에 대한 설명과 구체적인 예시를 4-5문장으로 추출하세요.
5. 핵심 내용과 설명, 구체적인 예시를 체계적으로 정리하여 "3. 세부 요약"에 적으세요.
6. 전체 내용을 3개 문장으로 요약하여, "2. 전체 요약"에 넣으세요.

## 주의사항
- 반드시 한국어로 작성한다.
- 반드시 문서에 있는 내용만을 활용하여 요약하세요.

## 문서 내용
{document_content}"""

current_prompt = DEFAULT_PROMPT
current_system_prompt = "당신은 문서를 요약하는 전문가입니다. 문서를 잘 확인하고, 사용자가 전체적인 내용을 쉽게 파악할 수 있도록 요약하세요."
current_model = "gpt-5-mini"

def update_prompt(prompt):
    global current_prompt
    current_prompt = prompt if prompt.strip() else DEFAULT_PROMPT
    return "요약 프롬프트가 업데이트되었습니다."

def update_system_prompt(system_prompt):
    global current_system_prompt
    current_system_prompt = system_prompt if system_prompt.strip() else "당신은 문서를 요약하는 전문가입니다. 문서를 잘 확인하고, 사용자가 전체적인 내용을 쉽게 파악할 수 있도록 요약하세요."
    return "시스템 프롬프트가 업데이트되었습니다."

def update_model(model):
    global current_system_prompt
    current_model = model if model.strip() else "gpt-5-mini"

def parse_pdf_and_summarize(file):
    try:
        if file is None:
            return "파일을 업로드해주세요."

        file_path = file.name
        file_name = os.path.basename(file_path)

        if not file_name.endswith(".pdf"):
            return "PDF 파일만 업로드 가능합니다."

        saved_file_path = os.path.join(input_dir, file_name)
        shutil.copy(file_path, saved_file_path)
        
        with open(saved_file_path, "rb") as f:   
            files = {"document": f}
            data = {
                    "ocr": "force",
                    "model": "document-parse",
                    "output_formats": "['markdown']"
            }
            response = requests.post(url, headers=headers, files=files, data=data)
            result = response.json()
            
        markdown_content = result["content"]["markdown"]
        markdown_file_path = os.path.join(parsed_dir, file_name.replace(".pdf", "_parsed.md"))
        with open(markdown_file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        # 현재 설정된 프롬프트 사용
        prompt_template = current_prompt

        # {document_content} 플레이스홀더를 실제 내용으로 치환
        if "{document_content}" in prompt_template:
            final_prompt = prompt_template.format(document_content=markdown_content[:8000])
        else:
            # 플레이스홀더가 없으면 프롬프트 끝에 문서 내용 추가
            final_prompt = f"{prompt_template}\n\n{markdown_content[:8000]}"
            
        completion = client.chat.completions.create(
            model=current_model,
            messages=[
                {"role": "system", "content": current_system_prompt},
                {"role": "user", "content": final_prompt}]
        )

        summary = completion.choices[0].message.content
        return summary

    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

def load_default_prompt():
    return DEFAULT_PROMPT

def load_default_system():
    return "당신은 문서를 요약하는 전문가입니다. 문서를 잘 확인하고, 사용자가 전체적인 내용을 쉽게 파악할 수 있도록 요약하세요."

def load_default_model():
    return "gpt-5-mini"

with gr.Blocks() as demo:
    gr.Markdown("# 📄 PDF 문서 파싱 및 요약 도구")
    gr.Markdown("PDF 문서를 업로드하고 사용자 정의 프롬프트로 요약을 생성하세요.")
    gr.Markdown("""### 🤖 사용 가능한 모델 :
    ```
    - gpt-5
    - gpt-5-mini (기본)
    - gpt-5-nano
    - gpt-4.1
    - gpt-4.1-mini
    - gpt-4.1-nano
    ```
    """)
    
    # 사용법 안내
    gr.Markdown("""
    ### 📋 사용법
    ```
    1. **GPT 모델**: '사용 가능한 모델' 중 하나를 선택합니다. 기본 모델은 gpt-5-mini로 설정되어 있습니다.
    2. **시스템 프롬프트**: GPT의 역할을 정의합니다. "기본 시스템 프롬프트 불러오기"를 통해 기본값 프롬프트를 사용할 수 있습니다.
    3. **요약 프롬프트**: 구체적인 요약 방법을 지정합니다. "기본 요약 프롬프트 불러오기"를 통해 기본값 프롬프트를 사용할 수 있습니다.
    - **{document_content}**: 이 부분에 문서 내용이 삽입됩니다.
    4. 프롬프트를 수정할 경우, "적용" 버튼을 눌러주세요. "시스템 프롬프트가 업데이트되었습니다." 또는 "요약 프롬프트가 업데이트되었습니다."는 메시지가 뜨면 수정된 프롬프트로 테스트할 수 있습니다.
    5. PDF 파일을 업로드하고 "업로드 & 요약"을 클릭하세요.
    ```

    ### 💡 프롬프트 예시
    ```
    "다음 문서의 내용을 요약하세요. {document_content}"
    ```
    """)
    
    with gr.Row():
        model_info_input = gr.Textbox(
            label="GPT 모델",
            placeholder=" gpt-5-mini",
            lines=1,
            value=""
        )
    
    with gr.Row():
        model_update_btn = gr.Button("🤖 모델 적용")
        model_load_btn = gr.Button("🤖 기본 모델 불러오기")

    # 프롬프트 설정 섹션
    with gr.Row():
        system_prompt_input = gr.Textbox(
            label="🤖 시스템 프롬프트",
            placeholder="GPT에게 역할을 부여하는 시스템 메시지를 입력하세요",
            lines=3,
            value=""
        )
    
    with gr.Row():
        system_update_btn = gr.Button("🤖 시스템 프롬프트 적용")
        system_load_btn = gr.Button("🤖 기본 시스템 프롬프트 불러오기")
    
    with gr.Row():
        system_status = gr.Textbox(label="시스템 프롬프트 상태", interactive=False)
    
    with gr.Row():
        custom_prompt_input = gr.Textbox(
            label="✏️ 사용자 정의 프롬프트",
            placeholder="원하는 분석 방식을 입력하세요. {document_content}를 사용하여 문서 내용이 삽입될 위치를 지정할 수 있습니다.",
            lines=10,
            value=""
        )
    
    with gr.Row():
        prompt_update_btn = gr.Button("✏️ 요약 프롬프트 적용")
        prompt_load_btn = gr.Button("📝 기본 요약 프롬프트 불러오기")
    
    with gr.Row():
        prompt_status = gr.Textbox(label="요약 프롬프트 상태", interactive=False)
    
    # 파일 업로드 및 처리 섹션
    with gr.Row():
        pdf_upload = gr.File(label="📂 PDF 파일 업로드")
    
    with gr.Row():
        upload_btn = gr.Button("📤 업로드 & 요약")
    
    with gr.Row():
        output_text = gr.Textbox(label="📌 요약 결과", lines=30)

    # 이벤트 연결
    model_update_btn.click(update_model, inputs=[model_info_input])
    model_load_btn.click(load_default_model, outputs=[model_info_input])

    system_update_btn.click(update_system_prompt, inputs=[system_prompt_input], outputs=[system_status])
    system_load_btn.click(load_default_system, outputs=[system_prompt_input])
    
    prompt_update_btn.click(update_prompt, inputs=[custom_prompt_input], outputs=[prompt_status])
    prompt_load_btn.click(load_default_prompt, outputs=[custom_prompt_input])
    
    upload_btn.click(parse_pdf_and_summarize, inputs=[pdf_upload], outputs=[output_text])
    


# 🔹 실행
if __name__ == "__main__":
    demo.launch(share=True)