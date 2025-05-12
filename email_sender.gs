function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('이메일 송부')
    .addItem('이메일 보내기', 'sendInstructorEmails')
    .addToUi();
}

function sendInstructorEmails() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  let data = sheet.getDataRange().getValues(); // const에서 let으로 변경

  // 시트에 데이터가 없는 경우, 헤더 자동 생성
  if (data.length === 0 || data[0].length === 0) {
    sheet.getRange(1, 1, 1, 9).setValues([[
      "강사명", "연락번호", "이메일", "일자리분야", "과정명", "이메일발송일자", "발송여부", "강의확인서 Only", "발송보류"
    ]]);
    SpreadsheetApp.getUi().alert("헤더가 생성되었습니다. 데이터를 입력 후 다시 실행하세요.");
    return;
  }

  // 헤더 확인
  let header = data[0]; // const에서 let으로 변경
  Logger.log("헤더: " + header.join(", "));

  // 헤더 정규화 및 인덱스 찾기
  const normalizeHeader = (header) => header.trim().toLowerCase();
  const requiredHeaders = ['이름', '이메일', '공통서류링크', '강의확인서링크'];
  const optionalHeaders = ['강의확인서 Only', '발송보류'];
  let headerRow = data[0]; // const에서 let으로 변경
  
  // 헤더 인덱스 찾기 - 여러 가지 헤더 이름 지원
  // 새로운 헤더 구조: 강사명, 연락번호, 이메일, 일자리분야, 과정명, 이메일발송일자, 발송여부, 강의확인서 Only, 발송보류
  const nameCol = headerRow.indexOf('강사명');
  const emailCol = headerRow.indexOf('이메일');
  
  // 일자리분야와 과정명 헤더 찾기
  let jobFieldCol = headerRow.indexOf('일자리분야');
  let courseNameCol = headerRow.indexOf('과정명');
  
  // 기본 링크 설정
  const defaultCommonLink = "https://docs.google.com/spreadsheets/d/1l-nzSkIwpgHFfaDdqPoKWeK2HvhyxIKxCbNcz2oesDk/edit";
  const defaultLectureLink = "https://docs.google.com/spreadsheets/d/11aZgFXTqlN9Kn2sktJP2Nqopgdp2G05ZIBjaaRykZsI/edit";
  // 헤더 이름을 두 가지 방식으로 찾기: 정확한 일치와 대소문자 무관 일치
  const lectureOnlyCol = headerRow.indexOf('강의확인서 Only') !== -1 ? 
    headerRow.indexOf('강의확인서 Only') : 
    header.findIndex(h => normalizeHeader(h) === "강의확인서 only");
  
  const holdSendingCol = headerRow.indexOf('발송보류');
  
  // 발송여부 열 추가
  const sentStatusCol = headerRow.indexOf('발송여부');
  const sendDateCol = headerRow.indexOf('이메일발송일자');

  // 누락된 헤더 확인
  let missingHeaders = [];
  if (nameCol === -1) missingHeaders.push("이름/강사명");
  if (emailCol === -1) missingHeaders.push("이메일");
  
  // 헤더가 없으면 자동으로 추가
  if (jobFieldCol === -1) {
    // 일자리분야 헤더 추가
    sheet.getRange(1, 4).setValue("일자리분야");
    jobFieldCol = 3; // 0부터 시작하므로 D열은 인덱스 3
    Logger.log("일자리분야 헤더가 없어 추가했습니다.");
  }
  
  if (courseNameCol === -1) {
    // 과정명 헤더 추가
    sheet.getRange(1, 5).setValue("과정명");
    courseNameCol = 4; // 0부터 시작하므로 E열은 인덱스 4
    Logger.log("과정명 헤더가 없어 추가했습니다.");
  }

  if (missingHeaders.length > 0) {
    SpreadsheetApp.getUi().alert(`다음 필수 헤더가 누락되었습니다: ${missingHeaders.join(", ")}
헤더를 확인하세요.`);
    return;
  }
  
  // 헤더 추가된 경우 다시 데이터 가져오기
  data = sheet.getDataRange().getValues();
  header = data[0];
  // 헤더로우도 다시 가져오기
  headerRow = data[0];

  const replyTo = "hana2nd@sangsangwoori.com";
  let count = 0;
  let errors = [];

  // 처리할 유효한 행 필터링
  let validRows = [];
  for (let row = 1; row < data.length; row++) {
    const name = data[row][nameCol];
    const email = data[row][emailCol];

    // 이름 또는 이메일이 없으면 건너뛰기
    if (!name || !email || name.trim() === "" || email.trim() === "") {
      // 비어 있는 행은 오류 메시지 출력하지 않고 그냥 건너뛀
      continue;
    }

    // 이메일 형식 검증
    if (!isValidEmail(email)) {
      errors.push(`행 ${row + 1}: 이메일 형식이 잘못됨 (${email})`);
      continue;
    }

    // 유효한 행 추가
    validRows.push(row);
  }

  Logger.log(`처리할 유효한 행: ${validRows.length}개`);

  // 유효한 행만 처리
  for (const row of validRows) {
    const name = data[row][nameCol];
    const email = data[row][emailCol];
    // 일자리분야와 과정명 정보 가져오기 (링크로 사용하지 않음)
    const jobField = data[row][jobFieldCol] || "";
    const courseName = data[row][courseNameCol] || "";
    
    // 강의확인서 Only 체크박스 상태 확인
    let lectureOnly = false;
    if (lectureOnlyCol !== -1) {
      lectureOnly = data[row][lectureOnlyCol] === true;
      Logger.log(`행 ${row + 1}: 강의확인서 Only = ${lectureOnly}`);
    }
    
    // 발송보류 체크박스 상태 확인
    let holdSending = false;
    if (holdSendingCol !== -1) {
      holdSending = data[row][holdSendingCol] === true;
      Logger.log(`행 ${row + 1}: 발송보류 = ${holdSending}`);
    }
    
    // 발송보류가 체크되어 있으면 이메일 발송하지 않음
    if (holdSending) {
      errors.push(`행 ${row + 1}: 발송보류가 체크되어 있어 이메일을 발송하지 않습니다.`);
      continue; // 다음 행으로 넘어감
    }

    // 기본 링크 설정
    const defaultCommonLink = "https://docs.google.com/spreadsheets/d/1l-nzSkIwpgHFfaDdqPoKWeK2HvhyxIKxCbNcz2oesDk/edit";
    const defaultLectureLink = "https://docs.google.com/spreadsheets/d/11aZgFXTqlN9Kn2sktJP2Nqopgdp2G05ZIBjaaRykZsI/edit";
    const defaultPPTLink = "https://drive.google.com/file/d/1Hac_nY7nc7kyd9Z09fojeEA4J127_XdCSu8Dhg-TznY/view";
    const defaultFontsLink = "https://drive.google.com/file/d/182_ZEMQq6Swq1q10oFcCmCk4obRV-g6e/view";
    
    // 공통서류링크와 강의확인서링크는 기본 링크 사용
    const commonLinkText = `<a href="${defaultCommonLink}" target="_blank">공통서류 (1회 제출)</a>`;
    const lectureLinkText = `<a href="${defaultLectureLink}" target="_blank">강의확인서 (출강 시 제출)</a>`;
    
    // 로그에 일자리분야와 과정명 정보 출력
    Logger.log(`행 ${row + 1}: 일자리분야 = ${jobField}, 과정명 = ${courseName}`);
    
    // 링크는 기본 링크를 사용하므로 유효성 검사는 필요 없음

    // 디버깅 로그
    Logger.log(`행 ${row + 1} - 이름: ${name}, 이메일: ${email}, 강의확인서 Only: ${lectureOnly}`);

    // 강의확인서 Only 체크박스 상태에 따라 제목과 내용 변경
    let subject, htmlBody;
    
    if (lectureOnly) {
      subject = `[상상우리] ${name} 강사님, (${jobField}/${courseName}) 강의확인서 전달드립니다`;
      htmlBody = `
<html>
<head>
<style>
  a { color: #1a73e8; text-decoration: underline; }
</style>
</head>
<body>
  <p>안녕하세요, ${name} 강사님.</p>
  <p>하나 파워 온 세컨드 라이프 교육 관련 강의확인서를 전달드립니다.</p>

  <ul>
    <li>${lectureLinkText}</li>
  </ul>

  <p>작성 후 회신 부탁드립니다.<br>감사합니다.</p>

  <p>- 상상우리 드림</p>
</body>
</html>`;
    } else {
      subject = `[상상우리] ${name} 강사님, (${jobField}/${courseName}) 교육 관련 서류를 전달드립니다`;
      htmlBody = `
<html>
<head>
<style>
  a { color: #1a73e8; text-decoration: underline; }
</style>
</head>
<body>
  <p>안녕하세요, ${name} 강사님.</p>
  <p>하나 파워 온 세컨드 라이프 교육 관련 제출 서류 및 자료를 전달드립니다.</p>

  <ul>
    <li>${commonLinkText}</li>
    <li>${lectureLinkText}</li>
    <li><a href="${defaultPPTLink}" target="_blank">교재 템플릿 (PPT)</a></li>
    <li><a href="${defaultFontsLink}" target="_blank">Hana Fonts (Zip)</a></li>
  </ul>

  <p>작성 후 회신 부탁드립니다.<br>감사합니다.</p>

  <p>- 상상우리 드림</p>
</body>
</html>`;
    }

    // 이메일 전송
    try {
      GmailApp.sendEmail(email, subject, "", {
        htmlBody: htmlBody,
        replyTo: replyTo
      });

      // 이메일 발송일자와 발송여부 기록
      if (sendDateCol !== -1) {
        sheet.getRange(row + 1, sendDateCol + 1).setValue(Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm"));
      }
      if (sentStatusCol !== -1) {
        sheet.getRange(row + 1, sentStatusCol + 1).setValue("발송완료");
      }

      count++;
      Logger.log(`행 ${row + 1}: 이메일 발송 성공 (${email})`);
    } catch (e) {
      errors.push(`행 ${row + 1}: 이메일 전송 오류 (${email}): ${e.message}`);
    }
  }

  // 결과 메시지
  let message = `총 ${count}건의 이메일을 성공적으로 발송했습니다.`;
  if (errors.length > 0) {
    message += `\n\n오류:\n${errors.join('\n')}`;
  }
  SpreadsheetApp.getUi().alert(message);
}

// URL 유효성 검사 함수
function isValidURL(url) {
  if (!url || typeof url !== 'string') return false;
  // 구글 드라이브 URL 패턴 (더 유연하게 수정)
  return url.trim().startsWith('https://');
}

// 이메일 형식 검사 함수
function isValidEmail(email) {
  if (!email || typeof email !== 'string') return false;
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
}
