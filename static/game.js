const board = document.getElementById("board");
const ctx = board.getContext("2d");
const scoreEl = document.getElementById("score");
const stateEl = document.getElementById("state");
const form = document.getElementById("submit");
const messageEl = document.getElementById("message");

const SIZE = 20;
const CELL = board.width / SIZE;
const DIRECTIONS = { ArrowUp: "up", ArrowDown: "down", ArrowLeft: "left", ArrowRight: "right" };
let state = null;
let timer = null;

function fresh() {
  return {
    body: [[10, 10], [9, 10], [8, 10]],
    dir: "right",
    alive: true,
    score: 0,
    food: [14, 10],
  };
}

function draw() {
  ctx.clearRect(0, 0, board.width, board.height);
  ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--line");
  ctx.lineWidth = 1;
  if (state) {
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--accent");
    for (const [x, y] of state.body) {
      ctx.fillRect(x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2);
    }
    if (state.food) {
      ctx.fillRect(state.food[0] * CELL + 6, state.food[1] * CELL + 6, CELL - 12, CELL - 12);
    }
  }
}

function tick() {
  if (!state || !state.alive) return;
  const delta = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] }[state.dir];
  const head = [state.body[0][0] + delta[0], state.body[0][1] + delta[1]];
  if (head[0] < 0 || head[1] < 0 || head[0] >= SIZE || head[1] >= SIZE ||
      state.body.slice(0, -1).some(([x, y]) => x === head[0] && y === head[1])) {
    gameOver();
    return;
  }
  if (state.food && head[0] === state.food[0] && head[1] === state.food[1]) {
    state.body.unshift(head);
    state.score += 10;
    state.food = randomFood();
  } else {
    state.body.unshift(head);
    state.body.pop();
  }
  scoreEl.textContent = String(state.score);
  draw();
}

function randomFood() {
  const taken = new Set(state.body.map(([x, y]) => `${x},${y}`));
  const free = [];
  for (let y = 0; y < SIZE; y += 1) for (let x = 0; x < SIZE; x += 1) {
    if (!taken.has(`${x},${y}`)) free.push([x, y]);
  }
  return free.length ? free[Math.floor(Math.random() * free.length)] : null;
}

function start() {
  state = fresh();
  state.food = randomFood();
  scoreEl.textContent = "0";
  stateEl.textContent = "进行中";
  form.hidden = true;
  messageEl.textContent = "";
  clearInterval(timer);
  timer = setInterval(tick, 140);
  draw();
}

function gameOver() {
  state.alive = false;
  clearInterval(timer);
  stateEl.textContent = "游戏结束";
  form.hidden = false;
}

document.addEventListener("keydown", (event) => {
  if (event.code === "Space") { event.preventDefault(); start(); return; }
  const dir = DIRECTIONS[event.key];
  if (!dir || !state || !state.alive) return;
  const opposite = { up: "down", down: "up", left: "right", right: "left" }[state.dir];
  if (dir !== opposite) state.dir = dir;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = document.getElementById("name").value.trim();
  const response = await fetch("/api/score", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, score: state.score }),
  });
  messageEl.textContent = response.ok ? "分数已保存" : "保存失败";
});

draw();
