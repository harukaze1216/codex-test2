const STORAGE_KEY = "task-manager-tasks";

const state = {
  tasks: [],
  showCompleted: false,
};

const $ = (selector) => document.querySelector(selector);
const newTaskForm = $("#new-task-form");
const titleInput = $("#task-title");
const descriptionInput = $("#task-description");
const showCompletedToggle = $("#show-completed");
const clearCompletedButton = $("#clear-completed");
const taskList = $("#task-list");
const emptyState = $("#empty-state");
const template = $("#task-item-template");

const formatter = new Intl.DateTimeFormat(undefined, {
  dateStyle: "medium",
  timeStyle: "short",
});

function loadTasks() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      state.tasks = [];
      return;
    }
    const parsed = JSON.parse(stored);
    if (!Array.isArray(parsed)) {
      throw new Error("Invalid task data");
    }
    state.tasks = parsed.map((task) => ({
      title: String(task.title ?? ""),
      description: String(task.description ?? ""),
      completed: Boolean(task.completed),
      createdAt: task.createdAt ?? new Date().toISOString(),
      completedAt: task.completedAt ?? null,
    }));
  } catch (error) {
    console.error("Failed to load tasks", error);
    state.tasks = [];
  }
}

function persistTasks() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.tasks));
}

function updateEmptyState() {
  const visibleTasks = state.tasks.filter((task) => state.showCompleted || !task.completed);
  emptyState.hidden = visibleTasks.length > 0;
  taskList.hidden = visibleTasks.length === 0;
}

function renderTasks() {
  taskList.innerHTML = "";
  const visibleTasks = state.tasks.filter((task) => state.showCompleted || !task.completed);

  visibleTasks.forEach((task) => {
    const actualIndex = state.tasks.indexOf(task);
    const content = template.content.cloneNode(true);
    const element = content.querySelector(".task");
    element.dataset.index = actualIndex;

    if (task.completed) {
      element.classList.add("completed");
    }

    const indexElement = content.querySelector(".task__index");
    indexElement.textContent = actualIndex;

    const titleElement = content.querySelector(".task__title");
    titleElement.textContent = task.title;

    const statusBadge = document.createElement("span");
    statusBadge.className = "status";
    statusBadge.textContent = task.completed ? "完了" : "未完了";
    titleElement.appendChild(statusBadge);

    const descriptionElement = content.querySelector(".task__description");
    descriptionElement.textContent = task.description;

    const metaElement = content.querySelector(".task__meta");
    const createdInfo = document.createElement("span");
    createdInfo.textContent = `作成: ${formatter.format(new Date(task.createdAt))}`;
    metaElement.appendChild(createdInfo);

    if (task.completed && task.completedAt) {
      const completedInfo = document.createElement("span");
      completedInfo.textContent = `完了: ${formatter.format(new Date(task.completedAt))}`;
      metaElement.appendChild(completedInfo);
    }

    const completeButton = content.querySelector(".complete");
    const deleteButton = content.querySelector(".delete");

    completeButton.addEventListener("click", () => completeTask(actualIndex));
    deleteButton.addEventListener("click", () => deleteTask(actualIndex));

    if (task.completed) {
      completeButton.disabled = true;
    }

    taskList.appendChild(content);
  });

  updateEmptyState();
  updateClearCompletedButton();
}

function addTask(title, description) {
  state.tasks.push({
    title,
    description,
    completed: false,
    createdAt: new Date().toISOString(),
    completedAt: null,
  });
  persistTasks();
  renderTasks();
}

function completeTask(index) {
  const task = state.tasks[index];
  if (!task || task.completed) {
    return;
  }
  task.completed = true;
  task.completedAt = new Date().toISOString();
  persistTasks();
  renderTasks();
}

function deleteTask(index) {
  state.tasks.splice(index, 1);
  persistTasks();
  renderTasks();
}

function clearCompleted() {
  state.tasks = state.tasks.filter((task) => !task.completed);
  persistTasks();
  renderTasks();
}

function updateClearCompletedButton() {
  const hasCompleted = state.tasks.some((task) => task.completed);
  clearCompletedButton.disabled = !hasCompleted;
}

function handleFormSubmit(event) {
  event.preventDefault();
  const title = titleInput.value.trim();
  const description = descriptionInput.value.trim();
  if (!title) {
    titleInput.focus();
    return;
  }
  addTask(title, description);
  newTaskForm.reset();
  titleInput.focus();
}

function init() {
  loadTasks();
  renderTasks();

  newTaskForm.addEventListener("submit", handleFormSubmit);

  showCompletedToggle.addEventListener("change", (event) => {
    state.showCompleted = event.target.checked;
    renderTasks();
  });

  clearCompletedButton.addEventListener("click", clearCompleted);

  window.addEventListener("storage", (event) => {
    if (event.key === STORAGE_KEY) {
      loadTasks();
      renderTasks();
    }
  });
}

document.addEventListener("DOMContentLoaded", init);
