# ElevenLabs 설정과 실행

Voice ID: `1PdAOcPlPTz12RwMyFVp` (메시지 끝 역슬래시 제외). 기본 모델 `eleven_multilingual_v2`. 수치는 청취 전 시작값이며 음성 적합성을 보장하지 않는다.
공식 API: https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps (2026-10-24 확인).
POST `/v1/text-to-speech/{voice_id}/with-timestamps`, `xi-api-key` 인증. MP3와 문자 타이밍을 저장한다. 이 모델에는 language_code를 보내지 않는다. 기본 `mp3_44100_128` 사용.

```powershell
python Skills-common/skills/cloudike-service-video/scripts/elevenlabs_tts.py --check
python Skills-common/skills/cloudike-service-video/scripts/elevenlabs_tts.py --text-file outputs/cloudike-video/scene01.txt --out-prefix outputs/cloudike-video/audio/scene01
```

--check는 로컬 키 로딩만 확인하며 API 요청·과금이 없다. 합성은 영상 제작 요청 시 실행한다. UTF-8 대본을 장면별로 제공한다. 환경 변수 ELEVENLABS_API_KEY를 우선하고, 없으면 작업공간 `.secrets/cloudike-video/elevenlabs.dpapi`를 읽는다. ELEVENLABS_KEY_FILE로 경로를 변경할 수 있다. DPAPI 파일은 현재 Windows 사용자/컴퓨터 전용이며 배포·압축·버전 관리에서 제외한다. 다른 환경에서는 키를 별도 설정한다.
제품명은 직접 듣고 발음을 조정한다. alignment.json의 실제 타이밍에 장면·SRT를 맞추고 강조 자막은 별도로 편집한다. 같은 대본의 음성을 재사용한다. 401/403/429·네트워크 오류는 자동 재시도하지 않는다. 음성 권한 오류 시 다른 Voice로 대체하지 않는다.

## 씬 전환의 첫음 중복 방지
씬 사이에 호흡이나 체류 시간을 넣는 영상은 씬별 독립 TTS 파일을 기본으로 사용한다. 각 파일에는 해당 씬 대본만 넣고 같은 Voice·모델·설정을 유지한다. 전체 음성을 먼저 속도 변경한 뒤 원본 문자 타이밍을 단순 비례 환산해 자르지 않는다. 시간 늘이기는 파형 위치를 정확한 선형 비율로 보장하지 않는다.
독립 파일 전체를 속도 조정하고 실제 PCM 길이로 배치한다. 파일 앞뒤 4~5ms 램프는 클릭 제거에만 사용하고 발음 중간에 페이드하지 않는다. 다음 씬 첫 음절을 앞 씬 여백으로 끌어오지 않는다.
연속 원본을 꼭 분할해야 하면 속도 변경 전에 원본 PCM의 실제 무음 경계에서 한 번만 나누고, 인접 구간이 겹치지 않는지 검증한다. 자막/화면은 최종 음성 배치에 다시 맞춘다. 씬 전환 전후 구간을 별도 검수 파일로 추출해 첫음 반복·마지막 음절 잘림·호흡 단절을 점검한다. 직접 청취하지 못했다면 청취 완료라고 쓰지 않는다.
