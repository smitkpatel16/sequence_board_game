"use strict";
var gameSocket = null;
var chatId = null;
var personName = null;
var personID = null;
var image = null;
var master = false;
var teamName = null;
var images = [];
var myCards = [];
var board = [["Joker", "TS", "QS", "KS", "AS", "2D", "3D", "4D", "5D", "Joker"],
["9S", "TH", "9H", "8H", "7H", "6H", "5H", "4H", "3H", "6D"],
["8S", "QH", "7D", "8D", "9D", "TD", "QD", "KD", "2H", "7D"],
["7S", "KH", "6D", "2C", "AH", "KH", "QH", "AD", "2S", "8D"],
["6S", "AH", "5D", "3C", "4H", "3H", "TH", "AC", "3S", "9D"],
["5S", "2C", "4D", "4C", "5H", "2H", "9H", "KC", "4S", "TD"],
["4S", "3C", "3D", "5C", "6H", "7H", "8H", "QC", "5S", "QD"],
["3S", "4C", "2D", "6C", "7C", "8C", "9C", "TC", "6S", "KD"],
["2S", "5C", "AS", "KS", "QS", "TS", "9S", "8S", "7S", "AD"],
["Joker", "6C", "7C", "8C", "9C", "TC", "QC", "KC", "AC", "Joker"]]
var cardmap = {
  J: "Jack",
  Q: "Queen",
  K: "King",
  A: "Ace",
  2: "Two",
  3: "Three",
  4: "Four",
  5: "Five",
  6: "Six",
  7: "Seven",
  8: "Eight",
  9: "Nine",
  T: "Ten",
  H: "Hearts",
  S: "Spade",
  C: "Club",
  D: "Diamond"
}

function addImageProcess(src) {
  return new Promise((resolve, reject) => {
    let img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

function startGame() {
  if (gameSocket) {
    var obj = {}
    obj['gameID'] = chatId;
    obj['messageType'] = 'start';
    gameSocket.send(JSON.stringify(obj));
  }
}

function fix_dpi(id) {
  var canvas = document.getElementById(id);
  var dpi = window.devicePixelRatio;
  //create a style object that returns width and height
  let style = {
    height() {
      return +getComputedStyle(canvas).getPropertyValue('height').slice(0, -2);
    },
    width() {
      return +getComputedStyle(canvas).getPropertyValue('width').slice(0, -2);
    }
  }
  //set the correct attributes for a crystal clear image!
  canvas.setAttribute('width', style.width() * dpi);
  canvas.setAttribute('height', style.height() * dpi);
}


function drawCircle(e) {
  var can = document.getElementById("board");
  var canctx = can.getContext("2d");

  var pos = getCursorPosition(can, e);
  var clickX = pos.x;
  var clickY = pos.y;

  canctx.fillStyle = "#2980b9";
  canctx.beginPath();
  canctx.arc(clickX, clickY, 10, 0, 2 * Math.PI);
  canctx.fill();

  console.log(clickX, clickY);
  console.log("drawcircle");
}
function getCursorPosition(canvas, e) {
  // Gets click position
  var rect = canvas.getBoundingClientRect();

  console.log('getcursorpos');

  return {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  };
}

async function getChatID() {
  var url_string = window.location.href;
  var u = new URL(url_string);
  var el = document.getElementById("chatID");
  el.value = u.searchParams.get("id");
  var boardDiv = document.getElementById("board");
  // var ctx = c.getContext("2d");
  // ctx.imageSmoothingEnabled = false;
  // fix_dpi("board");
  // fix_dpi("myCards");
  for (var i = 0; i < 10; i++) {
    for (var j = 0; j < 10; j++) {
      var imgElement = document.getElementById(j.toString() + "_" + i.toString() + "_" + board[i][j]);
      var parentE = imgElement.parentElement;
      parentE.setAttribute("style", "width:" + Math.floor(boardDiv.clientWidth / 10.5).toString() + "px;height:" + (boardDiv.clientHeight / 10.5).toString() + "px;");
      imgElement.className = "free"
      parentE.id = j.toString() + "_" + i.toString() + "_" + board[i][j] + '_div'
      parentE.setAttribute("onclick", "imageClicked(this.id);")
    }
  }
}
function occupyCard(x, y, card, imgID) {
  var obj = {}
  obj.x = imgID.split("_")[0];
  obj.y = imgID.split("_")[1];
  obj.card = card;
  obj.gameID = chatId;
  obj.messageType = "occupy";
  obj.teamName = teamName;
  gameSocket.send(JSON.stringify(obj));
}
function freeCard(x, y, card, imgID) {
  var obj = {}
  obj.x = imgID.split("_")[0];
  obj.y = imgID.split("_")[1];
  obj.card = card;
  obj.gameID = chatId;
  obj.messageType = "free";
  obj.teamName = teamName;
  gameSocket.send(JSON.stringify(obj));
}
function imageClicked(imgID) {
  // JC and JD are TWO EYED and JH and JS are ONE EYED
  var iid = imgID.split("_")[0] + "_" + imgID.split("_")[1] + "_" + imgID.split("_")[2]
  var imgTag = document.getElementById(iid);
  var card = imgID.split("_")[2];
  if (imgTag.className == "free") {
    var c = confirm("Would you like to occupy " + cardmap[card.charAt(0)] + " of " + cardmap[card.charAt(1)] + " ?")
    if (c) {
      if (myCards.indexOf(card) >= 0) {
        occupyCard(imgID.split("_")[0], imgID.split("_")[1], card, iid);
      }
      else if (myCards.indexOf("JC") >= 0 || myCards.indexOf("JD") >= 0) {
        occupyCard(imgID.split("_")[0], imgID.split("_")[1], card, iid);
      }
      else {
        alert("You have no suitable card to pick from your deck");
      }
    }
  }
  if (imgTag.className == "occupied") {
    var c = confirm("Would you like to free " + cardmap[card.charAt(0)] + " of " + cardmap[card.charAt(1)] + " ?")
    if (myCards.indexOf("JH") >= 0 || myCards.indexOf("JS") >= 0) {
      freeCard(imgID.split("_")[0], imgID.split("_")[1], card, iid);
    }
    else {
      alert("You have no suitable card to pick from your deck");
    }

  }

}


function chatCollapse() {
  showStyle = "height: 50vh; overflow-y: scroll; border: 1px solid #333333;"
  var txtBlock = document.getElementById("chatMessages");
  if (txtBlock.style['cssText'] === "display: none;") {
    txtBlock.style = showStyle;
  }
  else {

    txtBlock.style = "display: none;";

  }
}
function joinRoom() {
  var el = document.getElementById("chatID");
  chatId = el.value;
  el = document.getElementById("personName");
  personName = el.value;
  if (chatId && personName) {
    if (gameSocket) {
      gameSocket.close();
    }
    window.history.pushState("", "", location.protocol + '//' + location.host + location.pathname + "?id=" + chatId);
    var wsURL = "ws://" + window.location.host + "/gamesocket";
    // console.log(window.location.host);
    gameSocket = new WebSocket(wsURL);
    gameSocket.onopen = function (evt) { onOpen(evt) };
    gameSocket.onclose = function (evt) { onClose(evt) };
    gameSocket.onmessage = function (evt) { onMessage(evt) };
    gameSocket.onerror = function (evt) { onError(evt) };
  }
  else {
    if (!personName && !chatId) {
      alert("Enter Name and Chat ID")
    }
    else {
      if (!personName) {
        alert("Enter Name")
      }
      else {
        if (!chatId) {
          alert("Enter Chat ID")
        }
      }
    }

  }
}

function sendMessage() {
  var el = document.getElementById("textMessage");
  if (el.value.trim() || image) {
    var obj = {};
    obj['gameID'] = chatId;
    obj['personName'] = personName;
    obj['messageType'] = 'text';
    obj['image'] = image;
    obj['message'] = el.value.trim();
    gameSocket.send(JSON.stringify(obj));
    el.value = "";
    cancelImage();
  }
  else {
    alert("Please enter a message");
  }
}
function onOpen(evt) {
  var el = document.getElementById("textMessage");
  el.removeAttribute("disabled");
  el = document.getElementById("sendMessage");
  el.removeAttribute("disabled");
  var obj = {};
  obj['joinRoom'] = chatId;
  obj['personName'] = personName
  gameSocket.send(JSON.stringify(obj));
}

function updateUnreadCount() {
  var str = document.getElementById("myModal2");
  if (!str.className.includes("show")) {
    var badge = document.getElementById("badge");
    var badgeCount = parseInt(badge.innerHTML);
    badgeCount = badgeCount + 1;
    badge.innerHTML = badgeCount;
  }
}
function removeUnreadCount() {
  var badge = document.getElementById("badge");
  badge.innerHTML = 0;
}


function onMessage(evt) {
  handleConference(evt.data).then(value => { console.log(value) });
}
function onError(evt) {
  console.log(evt);
}
function onClose(evt) {
  console.log("Chat Closed");
}
function cancelImage() {
  var output = document.getElementById('uploadImage');
  var cancel = document.getElementById('cancel');
  image = null;
  $('#uploadImage').val('');
  output.style = "display: none;"
  cancel.style = "display: none;"

}
var openImage = function (file) {
  var input = file.target;

  var reader = new FileReader();
  reader.onload = function () {
    var dataURL = reader.result;
    var output = document.getElementById('uploadImage');
    var cancel = document.getElementById('cancel');
    $("#file-input").val(null);
    output.src = dataURL;
    image = dataURL;
    output.style = "height:100px; width:100px;"
    cancel.style = "font-size:24px;color:red;background-color: Transparent;outline:none;"
  };
  reader.readAsDataURL(input.files[0]);
};
async function handleConference(messageStream) {
  var dataObj = JSON.parse(messageStream);
  if (dataObj['messageType'] == 'text') {
    var txtBlock = document.getElementById("chatMessages");
    var div = document.createElement("div");
    var b = document.createElement("b");
    var pre = document.createElement("pre");
    div.style = "border: 1px solid #eeeeee; background-color:rgba(00,00, 00, 0.3); color: #fff;";
    div.className = "chatimg"
    b.innerHTML = dataObj['messagePersonName'];
    pre.innerHTML = dataObj["message"];
    pre.style = "margin-bottom: 0; background-color:rgba(00,00, 00, 0.3); color: #fff;"
    div.append(b);
    if (dataObj["image"]) {
      var img = document.createElement("img");
      div.style = "border: 1px solid #eeeeee; background-color:rgba(00,00, 00, 0.3); color: #fff;";
      img.src = dataObj["image"];
      img.style = "width=90vw"
      div.append(img);
    }
    div.append(pre);
    txtBlock.append(div);
    txtBlock.scrollTop = txtBlock.scrollHeight;
    updateUnreadCount();
  }
  if (dataObj['messageType'] == 'init') {
    var el = document.getElementById("peopleInChat");
    while (el.firstChild) {
      el.removeChild(el.lastChild)
    }
    for (var person of dataObj['people']) {
      var div = document.createElement("div");
      div.innerHTML = person;
      el.appendChild(div);
    }
    personID = dataObj['id'];
  }
  if (dataObj['messageType'] == 'remove') {
    if (dataObj['peerId'] in peers) {
      var el = document.getElementById("peopleInChat");
      while (el.firstChild) {
        el.removeChild(el.lastChild)
      }
      for (var person of dataObj['people']) {
        var div = document.createElement("div");
        div.innerHTML = person;
        el.appendChild(div);
      }
    }
  }
  if (dataObj['messageType'] == 'start') {
    var cardDiv = document.getElementById("myCards");
    // var c = document.getElementById("myCards");
    // var ctx = c.getContext("2d");
    // c.height = dataObj['cards'].length * c.width * 1.52;
    // ctx.imageSmoothingEnabled = false;
    await fillCards(dataObj["cards"], cardDiv);
    teamName = dataObj["teamName"];

  }
  if (dataObj['messageType'] == 'occupy') {
    var imgTag = document.getElementById(dataObj["cardID"]);
    imgTag.className = "occupied";
    imgTag.parentElement.children[1].className = "overlayshow";
    imgTag.parentElement.children[1].style.background = dataObj["teamName"];
  }
  if (dataObj['messageType'] == 'free') {
    var imgTag = document.getElementById(dataObj["cardID"]);
    imgTag.className = "free";
    imgTag.parentElement.children[1].className = "overlay";
    imgTag.parentElement.children[1].style.background = dataObj["teamName"];
  }
  if (dataObj['messageType'] == 'newCard') {
    var cardDiv = document.getElementById("myCards");
    while (cardDiv.firstChild) {
      cardDiv.removeChild(cardDiv.lastChild);
    }
    await fillCards(dataObj["cards"], cardDiv);
  }

  return "Done";
}
async function fillCards(cards, cardDiv) {
  myCards = [];
  for (var i = 0; i < cards.length; i++) {
    myCards.push(cards[i]);
    var img = await addImageProcess("/static/images/FrontDeck/" + cards[i] + ".jpg");
    img.width = cardDiv.clientWidth;
    img.height = cardDiv.clientWidth * 1.52;
    cardDiv.append(img);
  }
}
function closeChat() {
  gameSocket.close();
}
function fail() {
  console.log("Failed");
}


window.addEventListener("load", getChatID, false);