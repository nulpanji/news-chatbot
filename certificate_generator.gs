const TEMPLATE_ID = '1avcWOdYmZ7FdYWKKsDY8CU9V-snBCvGApfTwjETCzDs'; // 수료증 템플릿 문서 ID
const FOLDER_ID = '1_WHBiPN5qu8x6pcH3_l9Yu_WKBdSPffm'; // 수료증 저장 폴더 ID

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('⚙️ 자동수료')
    .addItem('수료증 생성 실행', 'generateCertificates')
    .addToUi();
}

function generateCertificates() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("심화교육생 현황");
  const lastRow = sheet.getLastRow();
  const serialStart = 83; // 0083번부터 시작

  // 수료증 생성 대상 행 번호 리스트 생성
  let targets = [];
  for (let row = 9; row <= lastRow; row++) {
    const status = sheet.getRange(row, 22).getValue(); // V열: 수료여부
    const link = sheet.getRange(row, 37).getValue();   // AK열: 수료증 링크
    if (status === "수료" && link === "") {
      targets.push(row);
    }
  }

  // 일련번호 부여 및 수료증 생성
  for (let i = 0; i < targets.length; i++) {
    const row = targets[i];
    const serialNumber = String(serialStart + i).padStart(4, "0"); // 0083, 0084, ...
    const name = sheet.getRange(row, 14).getValue();
    const course = sheet.getRange(row, 8).getValue();
    const startDate = sheet.getRange(row, 4).getValue();
    const endDate = sheet.getRange(row, 5).getValue();

    const formattedStart = Utilities.formatDate(new Date(startDate), Session.getScriptTimeZone(), "yyyy년 MM월 dd일");
    const formattedEnd = Utilities.formatDate(new Date(endDate), Session.getScriptTimeZone(), "yyyy년 MM월 dd일");
    const period = `${formattedStart} ~ ${formattedEnd}`;
    const date = endDate;

    const docId = createCertificate(name, course, period, date, serialNumber);
    const url = `https://docs.google.com/document/d/${docId}/edit`;
    sheet.getRange(row, 37).setValue(url); // AK열에 수료증 링크 삽입
  }
}


function createCertificate(name, course, period, date, serialNumber, returnMonthInfo) {
  const template = DriveApp.getFileById(TEMPLATE_ID);

  // 종료일 기준 월 추출 (date: yyyy-MM-dd 또는 Date 객체)
  let month = "기타";
  if (date) {
    const d = new Date(date);
    const m = d.getMonth() + 1; // JS는 0~11월
    month = (m < 10 ? "0" : "") + m + "월";
  }

  // FOLDER_ID 하위에 'MM월' 폴더가 없으면 생성, 있으면 사용
  const parentFolder = DriveApp.getFolderById(FOLDER_ID);
  let monthFolder;
  const folders = parentFolder.getFoldersByName(month);
  if (folders.hasNext()) {
    monthFolder = folders.next();
  } else {
    monthFolder = parentFolder.createFolder(month);
  }

  // 해당 월 폴더에 복사본 생성
  const copy = template.makeCopy(`${name}_수료증`, monthFolder);
  const doc = DocumentApp.openById(copy.getId());
  const body = doc.getBody();

  const safeName = name || "이름 없음";
  const safeCourse = course || "과정 없음";
  const safePeriod = period || "기간 없음";
  const safeDate = date
    ? Utilities.formatDate(new Date(date), Session.getScriptTimeZone(), "yyyy년 MM월 dd일")
    : "날짜 없음";
  const safeSerial = serialNumber || "";

  body.replaceText("{{이름}}", safeName);
  body.replaceText("{{교육과정}}", safeCourse);
  body.replaceText("{{교육기간}}", safePeriod);
  body.replaceText("{{수료일자}}", safeDate);
  body.replaceText("{{일련번호}}", safeSerial);

  doc.saveAndClose();
  if (returnMonthInfo) {
    return {docId: copy.getId(), month: month, monthFolder: monthFolder};
  } else {
    return copy.getId();
  }
}

function testCreateOneCertificate() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("심화교육생 현황");
    const name = sheet.getRange(9, 14).getValue();     // N열: 이름
    const course = sheet.getRange(9, 8).getValue();    // H열: 교육과정명
    const startDate = sheet.getRange(9, 4).getValue(); // D열: 시작일
    const endDate = sheet.getRange(9, 5).getValue();   // E열: 종료일

    const formattedStart = Utilities.formatDate(new Date(startDate), Session.getScriptTimeZone(), "yyyy년 MM월 dd일");
    const formattedEnd = Utilities.formatDate(new Date(endDate), Session.getScriptTimeZone(), "yyyy년 MM월 dd일");
    const period = `${formattedStart} ~ ${formattedEnd}`;
    const date = endDate;

    const serialNumber = "0083"; // 테스트용 일련번호
    const docId = createCertificate(name, course, period, date, serialNumber);
    const url = `https://docs.google.com/document/d/${docId}/edit`;
    sheet.getRange(9, 37).setValue(url);
    Logger.log("수료증 링크 생성 완료: " + url);
  } catch (error) {
    Logger.log("⚠️ 오류 발생: " + error.message);
  }
}
