const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");

const BOT_MSGS = [
  "Hi, how are you?",
  "Ohh... I can't understand what you trying to say. Sorry!",
  "I like to play games... But I don't know how to play!",
  "Sorry if my answers are not relevant. :))",
  "I feel sleepy! :("
];

// Icons made by Freepik from www.flaticon.com
const BOT_IMG = "https://i.pinimg.com/originals/23/7e/7d/237e7dfccfe9c019bf148855aec83c11.gif";
const PERSON_IMG = "https://img.freepik.com/free-psd/3d-illustration-person-with-sunglasses_23-2149436188.jpg?t=st=1709990264~exp=1709993864~hmac=18bd8ea9c243b268da5f4b62cfcbae77c1868c3a8ed1985ef4429c69d1f3f0f1&w=740";
const BOT_NAME = "BOT";
const PERSON_NAME = "Chirag";
function handleButtonClick() {
  const userInput = document.getElementById('userInput').value;
  console.log("REQ DONE")
    event.preventDefault();

  const msgText = msgerInput.value;
  if (!msgText) return;

  appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
  msgerInput.value = "";
  botResponse(msgText);
}

function appendMessage(name, img, side, text) {
  //   Simple solution for small apps
  const msgHTML = `
    <div class="msg ${side}-msg">
      <div class="msg-img" style="background-image: url(${img})"></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${name}</div>
          <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text">${text}</div>
      </div>
    </div>
  `;

  msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  msgerChat.scrollTop += 500;
}

function botResponse(userText) {

  // Make AJAX request to Flask server
  $.ajax({
    url: '/get',
    data: { msg: userText },
    success: function(response) {
      const msgText = response;
      const delay = 0;

      setTimeout(() => {
        appendMessage(BOT_NAME, BOT_IMG, "left", msgText);
      }, delay);
    }
  });
}

// Utils
function get(selector, root = document) {
  return root.querySelector(selector);
}

function formatDate(date) {
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();

  return `${h.slice(-2)}:${m.slice(-2)}`;
}

function random(min, max) {
  return Math.floor(Math.random() * (max - min) + min);
}