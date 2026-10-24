# Cloudike 서비스 소개 영상 스킬

실제 Cloudike 홈페이지 화면과 공식 기능 자료를 바탕으로 기업용 소개 영상을 제작하는 Codex 스킬입니다.

- 기능별 공식 근거와 화면 출처 확인
- 화면 확대, 설명 상자, 자막, 전환, 음량 검수 기준
- 지정 ElevenLabs 음성과 문자 타이밍 생성 스크립트
- 씬별 독립 음성으로 다음 씬 첫소리 중복 방지
- 사람의 작업 흐름을 따르는 타이핑, 부드러운 마우스 이동, 클릭 표시와 스크롤 연출

## 사용

`skills/cloudike-service-video` 폴더를 사용하는 환경의 스킬 디렉터리에 복사한 뒤 호출합니다.

```text
$cloudike-service-video를 사용해 Cloudike 홈페이지 주요 기능을 소개하는 50초 기업용 영상을 제작해줘.
```

Python 3가 필요하며 음성 생성 스크립트는 표준 라이브러리를 사용합니다. 실제 화면 캡처와 영상 합성에는 해당 환경의 브라우저·편집·렌더링 도구가 별도로 필요합니다.

## 음성 설정

API 키는 실행 환경의 `ELEVENLABS_API_KEY`에 설정합니다. API 키, Windows DPAPI 저장소, 생성 영상·음성은 이 저장소에 포함되지 않습니다. Windows 로컬 저장소를 사용하는 경우 `ELEVENLABS_KEY_FILE`로 DPAPI 파일의 절대 경로를 지정할 수 있습니다.

지정 Voice ID: `1PdAOcPlPTz12RwMyFVp`. 해당 음성에 접근할 수 있는 ElevenLabs 계정이 필요합니다.

```powershell
python skills/cloudike-service-video/scripts/elevenlabs_tts.py --check
python skills/cloudike-service-video/scripts/elevenlabs_tts.py --text-file scene01.txt --out-prefix outputs/scene01
```

`--check`는 로컬 설정 확인만 수행합니다. 두 번째 명령은 실제 ElevenLabs 합성을 요청합니다. 씬마다 별도 대본 파일을 사용하고, 완성 음성의 실제 길이에 자막과 화면을 맞춥니다.

자세한 지침은 [SKILL.md](skills/cloudike-service-video/SKILL.md)에 있습니다. 영상 완성도는 사용한 화면 자료·실행 도구·최종 시청 및 청취 검수에 따라 달라집니다.
