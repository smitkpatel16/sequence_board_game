"use strict";
/* Global Variables */
var gameSocket = null;
var chatId = null;
var personName = null;
var personID = null;
var vph = null;
var vpw = null;
var image = null;
var master = false;
var teamName = null;
var teamWin = {}
var images = [];
var myCards = [];
var occupiedList = {
  '#0000ff90': [],
  '#00ff0090': [],
  '#ff000090': []
}
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
/* 
===============================================================================
 addImageProcess - adds the image and waits for it to load
=============================================================================== 
*/
function addImageProcess(src) {
  return new Promise((resolve, reject) => {
    let img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}
/* 
===============================================================================
 startGame - the master (first one in the room) can start the game
=============================================================================== 
*/
function startGame() {
  if (gameSocket) {
    var obj = {};
    obj['gameID'] = chatId;
    obj['messageType'] = 'start';
    gameSocket.send(JSON.stringify(obj));
  }
}
/* 
===============================================================================
 fixDPI - dpi and canvas are generally a mismatch showing blurred images
=============================================================================== 
*/
function fixDPI(id) {
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
/* 
===============================================================================
 getChatID - take chatID if present in URL
=============================================================================== 
*/
async function getChatID() {
  var url_string = window.location.href;
  var u = new URL(url_string);
  var el = document.getElementById("chatID");
  el.value = u.searchParams.get("id");
  await sortBoard();
}
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
async function sortBoard() {

  var orientation = window.screen.orientation || window.orientation;
  var orntn = null;
  if (orientation === "landscape-primary" || orientation === "landspace" || orientation === "landscape-secondary") {
    orntn = 'l';
  } else if (orientation === "portrait-secondary" || orientation === "portrait-primary" || orientation === "portrait") {
    orntn = 'p';
  } else if (orientation === undefined) {
    console.log("The orientation API isn't supported in this browser :(");
  }
  await sleep(1500);
  var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
  var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
  vph = h;
  vpw = w;
  if (w / h > 1) {
    orntn = 'l';
  }
  else {
    orntn = 'p';
  }
  var boardDiv = document.getElementById("board");
  if (orntn && orntn == 'l') {
    boardDiv.className = "col-12 board no-gutters"
  }
  else {
    boardDiv.className = "col-12 board no-gutters"
  }
  await sleep(500);
  //sort and arrange the board (this is just added here to do it always on page load)
  for (var i = 0; i < 10; i++) {
    for (var j = 0; j < 10; j++) {
      var imgElement = document.getElementById(j.toString() + "_" + i.toString() + "_" + board[i][j]);
      var parentE = imgElement.parentElement;
      if (orntn && orntn == 'l') {
        parentE.setAttribute("style", "width:" + Math.floor(boardDiv.clientWidth / 10).toString() + "px;height:" + (boardDiv.clientHeight / 10).toString() + "px;");
      }
      else {
        parentE.setAttribute("style", "width:" + Math.floor(boardDiv.clientWidth / 10).toString() + "px;height:" + (boardDiv.clientHeight / 10).toString() + "px;");
      }
      imgElement.className = "free";
      parentE.id = j.toString() + "_" + i.toString() + "_" + board[i][j] + '_div';
      parentE.setAttribute("onclick", "imageClicked(this.id);");
    }
  }
  if (myCards.length > 0) {
    var cardDiv = document.getElementById("myCards");
    // slice to pass by value
    await fillCards(myCards.slice(), cardDiv);
  }
}
/* 
===============================================================================
 occupyCard - occupy a card for a members turn
=============================================================================== 
*/
function occupyCard(x, y, card, imgID) {
  var obj = {};
  obj.x = imgID.split("_")[0];
  obj.y = imgID.split("_")[1];
  obj.card = card;
  obj.gameID = chatId;
  obj.messageType = "occupy";
  obj.teamName = teamName;
  gameSocket.send(JSON.stringify(obj));
}
/* 
===============================================================================
 freeCard - free up an occupied card for a members turn
=============================================================================== 
*/
function freeCard(x, y, card, imgID) {
  var obj = {};
  obj.x = imgID.split("_")[0];
  obj.y = imgID.split("_")[1];
  obj.card = card;
  obj.gameID = chatId;
  obj.messageType = "free";
  obj.teamName = teamName;
  gameSocket.send(JSON.stringify(obj));
}
/* 
===============================================================================
 imageClicked - trigger appropriate action on image clicked on board
=============================================================================== 
*/
function imageClicked(imgID) {
  // JC and JD are TWO EYED and JH and JS are ONE EYED
  var iid = imgID.split("_")[0] + "_" + imgID.split("_")[1] + "_" + imgID.split("_")[2];
  var imgTag = document.getElementById(iid);
  var card = imgID.split("_")[2];
  if (imgTag.className == "free") {
    var c = confirm("Would you like to occupy " + cardmap[card.charAt(0)] + " of " + cardmap[card.charAt(1)] + " ?");
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
    var c = confirm("Would you like to free " + cardmap[card.charAt(0)] + " of " + cardmap[card.charAt(1)] + " ?");
    if (myCards.indexOf("JH") >= 0 || myCards.indexOf("JS") >= 0) {
      freeCard(imgID.split("_")[0], imgID.split("_")[1], card, iid);
    }
    else {
      alert("You have no suitable card to pick from your deck");
    }
  }
}
/* 
===============================================================================
 joinRoom - join a play room
=============================================================================== 
*/
function joinRoom() {
  var el = document.getElementById("chatID");
  chatId = el.value;
  el = document.getElementById("personName");
  personName = el.value;
  if (chatId && personName) {
    if (gameSocket) {
      gameSocket.close();
    }
    var wsURL = null;
    window.history.pushState("", "", location.protocol + '//' + location.host + location.pathname + "?id=" + chatId);
    // if (location.protocol == 'http') {
    // wsURL = "ws://" + window.location.host + "/gamesocket";
    // }
    // else {
    wsURL = "ws://" + window.location.host + "/gamesocket";
    // }
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
/* 
===============================================================================
 sendMessage - send a chat message to the play room
=============================================================================== 
*/
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
/* 
===============================================================================
 onOpen - join socket
=============================================================================== 
*/
function onOpen(evt) {
  var el = document.getElementById("textMessage");
  el.removeAttribute("disabled");
  el = document.getElementById("sendMessage");
  el.removeAttribute("disabled");
  var obj = {};
  obj['joinRoom'] = chatId;
  obj['personName'] = personName;
  gameSocket.send(JSON.stringify(obj));
}
/* 
===============================================================================
 updateUnreadCount - when a new chat message arrives
=============================================================================== 
*/
function updateUnreadCount() {
  var str = document.getElementById("myModal2");
  if (!str.className.includes("show")) {
    var badge = document.getElementById("badge");
    var badgeCount = parseInt(badge.innerHTML);
    badgeCount = badgeCount + 1;
    badge.innerHTML = badgeCount;
  }
}
/* 
===============================================================================
 removeUnreadCount - when a chat window opens
=============================================================================== 
*/
function removeUnreadCount() {
  var badge = document.getElementById("badge");
  badge.innerHTML = 0;
}
/* 
===============================================================================
 onMessage - when message is received from socket
=============================================================================== 
*/
function onMessage(evt) {
  handleConference(evt.data).then(value => { console.log(value) });
}
/* 
===============================================================================
 onError - when error from socket
=============================================================================== 
*/
function onError(evt) {
  console.log(evt);
}
/* 
===============================================================================
 onClose - log when socket is closed
=============================================================================== 
*/
function onClose(evt) {
  console.log("Chat Closed");
}
/* 
===============================================================================
 cancelImage - cancel sending an image in chat
=============================================================================== 
*/
function cancelImage() {
  var output = document.getElementById('uploadImage');
  var cancel = document.getElementById('cancel');
  image = null;
  $('#uploadImage').val('');
  output.style = "display: none;"
  cancel.style = "display: none;"

}
/* 
===============================================================================
 openImage - attach an image
=============================================================================== 
*/
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
}
/* 
===============================================================================
 handleConference all socket messages arrive here
=============================================================================== 
*/
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
  //new person joins the game
  if (dataObj['messageType'] == 'init') {
    var el = document.getElementById("peopleInChat");
    while (el.firstChild) {
      el.removeChild(el.lastChild)
    }
    for (var person of dataObj['people']) {
      var div = document.createElement("div");
      div.innerHTML = person.split("_")[0];
      div.id = person.split("_")[1];
      el.appendChild(div);
    }
    personID = dataObj['id'];
  }
  //whose turn is it
  if (dataObj['messageType'] == 'turn') {
    var el = document.getElementById("peopleInChat");
    for (var i = 0; i < el.children.length; i++) {
      if (el.children[i].id == dataObj['memberid']) {
        console.log(el.children[i]);
        el.children[i].setAttribute("style", "background-color: " + dataObj['teamName'] + ";")
      }
      else {
        el.children[i].removeAttribute("style")
      }
    }
  }
  //a member got removed
  if (dataObj['messageType'] == 'remove') {
    var el = document.getElementById("peopleInChat");
    while (el.firstChild) {
      el.removeChild(el.lastChild)
    }
    for (var person of dataObj['people']) {
      var div = document.createElement("div");
      div.innerHTML = person.split("_")[0];
      div.id = person.split("_")[1];
      el.appendChild(div);
    }
    await resetBoard();
  }
  // start the game play
  if (dataObj['messageType'] == 'start') {
    var cardDiv = document.getElementById("myCards");
    // var c = document.getElementById("myCards");
    // var ctx = c.getContext("2d");
    // c.height = dataObj['cards'].length * c.width * 1.52;
    // ctx.imageSmoothingEnabled = false;
    await fillCards(dataObj["cards"], cardDiv);
    teamName = dataObj["teamName"];

  }
  // occupy a card
  if (dataObj['messageType'] == 'occupy') {
    var imgTag = document.getElementById(dataObj["cardID"]);
    imgTag.className = "occupied";
    imgTag.parentElement.children[1].className = "overlayshow";
    imgTag.parentElement.children[1].style.background = dataObj["teamName"];
  }
  if (dataObj['messageType'] == 'win') {
    for (var i = 0; i < 5; i++) {
      var imgTag = document.getElementById(dataObj["cardIDs"][i]);
      imgTag.className = "occupied-win";
      imgTag.parentElement.children[1].className = "overlayshowwin";
      imgTag.parentElement.children[1].style.background = dataObj["teamName"];
      if (!(dataObj["teamName"] in teamWin)) {
        teamWin[dataObj["teamName"]] = 1;
      }
      else {
        var winnerteam = null;
        switch (dataObj["teamName"]) {
          case "#0000ff":
            winnerteam = "Blue";
            break;
          case "#00ff00":
            winnerteam = "Green";
            break;
          case "#ff0000":
            winnerteam = "Read";
            break;

        }
        alert("Game Over " + winnerteam + " wins");
      }
    }
  }
  // free up an occupied card
  if (dataObj['messageType'] == 'free') {
    var imgTag = document.getElementById(dataObj["cardID"]);
    imgTag.className = "free";
    imgTag.parentElement.children[1].className = "overlay";
    imgTag.parentElement.children[1].style.background = dataObj["teamName"];
  }
  // new card for the current playing member
  if (dataObj['messageType'] == 'newCard') {
    var cardDiv = document.getElementById("myCards");
    while (cardDiv.firstChild) {
      cardDiv.removeChild(cardDiv.lastChild);
    }
    await fillCards(dataObj["cards"], cardDiv);
  }
  return "Done";
}
/* 
===============================================================================
 resetBoard reset the playing board to be blank
=============================================================================== 
*/
async function resetBoard() {
  var boardDiv = document.getElementById("board");
  var d = null;
  for (var i = 0; i < boardDiv.children.length; i++) {
    if (boardDiv.children[i].children[0]) {
      boardDiv.children[i].children[0].className = 'free';
      boardDiv.children[i].children[1].className = 'overlay';
    }
  }
  var cardDiv = document.getElementById("myCards");
  while (cardDiv.firstChild) {
    cardDiv.removeChild(cardDiv.lastChild);
  }
}
/* 
===============================================================================
 fillCards new cards for the player
=============================================================================== 
*/
async function fillCards(cards, cardDiv) {
  myCards = [];
  for (var i = 0; i < cards.length; i++) {
    myCards.push(cards[i]);
    var img = await addImageProcess("/static/images/FrontDeck/" + cards[i] + ".jpg");
    img.width = cardDiv.clientWidth / cards.length;
    img.height = cardDiv.clientHeight;
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
window.addEventListener("orientationchange", sortBoard, false);
