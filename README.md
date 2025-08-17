## pdf 문서 파싱 및 요약 (프롬프트 테스트용)

### 📂 문서 요약 및 파싱
- Upstage Document Parse를 통해 pdf 문서를 markdown으로 변환하고, 변환된 문서를 gpt를 이용하여 요약합니다. (document-parse, gpt-4o)
- 환경변수로 Upstage API key와 OpenAI API key가 필요합니다.

### 📂 프롬프트 테스트
- 직접 시스템 프롬프트와 요약 프롬프트를 작성하며 결과를 확인할 수 있습니다.
- 시스템 프롬프트와 요약 프롬프트의 예시를 기본값으로 작성해 두었습니다.
- 기본 프롬프트는 주로 짧은 논문 자료에 대한 한국어 요약문 생성을 고려하고 작성하였고, 첫 4000자만 활용하도록 설정하였습니다.

Upstage Document Parse API Reference :
https://console.upstage.ai/api/document-digitization/document-parsing

---
### 🤖 HuggingFace Demo :
https://huggingface.co/spaces/Cheeseorim/PDF_Summarize_Prompt_Test
