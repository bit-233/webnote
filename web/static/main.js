const state = {
  notes: [],
  currentId: null,
  authEnabled: false,
  listLoading: false,
};

const noteListEl = document.getElementById('noteList');
const titleInput = document.getElementById('titleInput');
const contentInput = document.getElementById('contentInput');
const tagsInput = document.getElementById('tagsInput');
const previewArea = document.getElementById('previewArea');
const searchInput = document.getElementById('searchInput');
const tagFilter = document.getElementById('tagFilter');
const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn');
const saveBtn = document.getElementById('saveBtn');
const deleteBtn = document.getElementById('deleteBtn');
const newNoteBtn = document.getElementById('newNoteBtn');
const toastContainer = document.getElementById('toastContainer');

async function fetchConfig() {
  const res = await fetch('/api/config');
  const data = await res.json();
  state.authEnabled = data.auth_enabled;
  loginBtn.style.display = state.authEnabled ? 'inline-block' : 'none';
  logoutBtn.style.display = state.authEnabled ? 'inline-block' : 'none';
}

function showToast(message, type = 'info', duration = 2400) {
  if (!toastContainer) return alert(message);
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('visible'));
  setTimeout(() => {
    toast.classList.remove('visible');
    setTimeout(() => toast.remove(), 200);
  }, duration);
}

function setListLoading(flag) {
  state.listLoading = flag;
  renderList();
}

function formattedTime(note) {
  const timeStr = note.updated_at || note.created_at;
  return timeStr ? new Date(timeStr).toLocaleString() : '';
}

function renderList(notes = state.notes) {
  noteListEl.innerHTML = '';
  if (state.listLoading) {
    noteListEl.innerHTML = '<li class="empty">加载中...</li>';
    return;
  }
  if (!notes.length) {
    const hasFilter = searchInput.value.trim() || tagFilter.value.trim();
    noteListEl.innerHTML = `<li class="empty">${hasFilter ? '没有符合条件的笔记' : '暂无笔记'}</li>`;
    return;
  }
  notes.forEach((note) => {
    const li = document.createElement('li');
    const title = document.createElement('div');
    title.className = 'note-title';
    title.textContent = note.title || '未命名笔记';

    const meta = document.createElement('div');
    meta.className = 'note-meta';
    meta.textContent = formattedTime(note);

    const tagsWrap = document.createElement('div');
    if (note.tags && note.tags.length) {
      note.tags.forEach((tag) => {
        const badge = document.createElement('span');
        badge.className = 'tag-badge';
        badge.textContent = tag;
        tagsWrap.appendChild(badge);
      });
    } else {
      const badge = document.createElement('span');
      badge.className = 'tag-badge empty';
      badge.textContent = '无标签';
      tagsWrap.appendChild(badge);
    }

    li.appendChild(title);
    li.appendChild(meta);
    li.appendChild(tagsWrap);
    li.onclick = () => loadNote(note.id);
    if (state.currentId === note.id) li.classList.add('active');
    noteListEl.appendChild(li);
  });
}

function currentPayload() {
  return {
    title: titleInput.value.trim(),
    content: contentInput.value,
    tags: tagsInput.value
      .split(',')
      .map((t) => t.trim())
      .filter((t) => t),
  };
}

async function loadNotes() {
  const params = new URLSearchParams();
  if (searchInput.value.trim()) params.append('query', searchInput.value.trim());
  if (tagFilter.value.trim()) params.append('tag', tagFilter.value.trim());
  setListLoading(true);
  try {
    const res = await fetch(`/api/notes?${params.toString()}`);
    if (!res.ok) {
      const err = await safeParse(res);
      showToast(err.detail || err.message || '加载笔记失败', 'error');
      return;
    }
    state.notes = await res.json();
  } catch (err) {
    showToast('加载笔记失败', 'error');
  } finally {
    setListLoading(false);
  }
}

async function loadNote(id) {
  try {
    const res = await fetch(`/api/notes/${id}`);
    if (!res.ok) {
      const err = await safeParse(res);
      showToast(err.detail || err.message || '加载失败', 'error');
      return;
    }
    const note = await res.json();
    state.currentId = note.id;
    titleInput.value = note.title;
    contentInput.value = note.content;
    tagsInput.value = (note.tags || []).join(',');
    updatePreview();
    renderList();
  } catch (err) {
    showToast('加载失败', 'error');
  }
}

function updatePreview() {
  const raw = contentInput.value;
  previewArea.innerHTML = marked.parse(raw || '');
}

async function saveNote() {
  const payload = currentPayload();
  const opts = {
    method: state.currentId ? 'PUT' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  };
  const url = state.currentId ? `/api/notes/${state.currentId}` : '/api/notes';
  const res = await fetch(url, opts);
  if (res.status === 401) return showToast('请先登录', 'error');
  if (!res.ok) {
    const err = await safeParse(res);
    return showToast(err.detail || err.message || '保存失败', 'error');
  }
  const note = await res.json();
  state.currentId = note.id;
  showToast('已保存', 'success');
  await loadNotes();
}

async function deleteNote() {
  if (!state.currentId) return showToast('请先选择笔记', 'info');
  if (!confirm('确认删除？')) return;
  const res = await fetch(`/api/notes/${state.currentId}`, { method: 'DELETE' });
  if (res.status === 401) return showToast('请先登录', 'error');
  if (!res.ok) {
    const err = await safeParse(res);
    return showToast(err.detail || err.message || '删除失败', 'error');
  }
  resetEditor();
  showToast('已删除', 'success');
  await loadNotes();
}

function resetEditor() {
  state.currentId = null;
  titleInput.value = '';
  contentInput.value = '';
  tagsInput.value = '';
  previewArea.innerHTML = '';
  renderList();
}

async function handleLogin() {
  const password = prompt('请输入管理密码');
  if (password === null) return;
  const form = new FormData();
  form.append('password', password);
  const res = await fetch('/api/login', { method: 'POST', body: form });
  if (!res.ok) {
    const err = await safeParse(res);
    return showToast(err.detail || err.message || '登录失败', 'error');
  }
  showToast('登录成功', 'success');
}

async function handleLogout() {
  const res = await fetch('/api/logout', { method: 'POST' });
  if (!res.ok) {
    const err = await safeParse(res);
    return showToast(err.detail || err.message || '登出失败', 'error');
  }
  showToast('已登出', 'success');
}

function bindEvents() {
  searchInput.addEventListener('input', () => loadNotes());
  tagFilter.addEventListener('input', () => loadNotes());
  contentInput.addEventListener('input', updatePreview);
  newNoteBtn.addEventListener('click', resetEditor);
  saveBtn.addEventListener('click', saveNote);
  deleteBtn.addEventListener('click', deleteNote);
  loginBtn.addEventListener('click', handleLogin);
  logoutBtn.addEventListener('click', handleLogout);
  window.addEventListener('keydown', handleShortcuts);
}

async function bootstrap() {
  bindEvents();
  await fetchConfig();
  await loadNotes();
  updatePreview();
}

function handleShortcuts(event) {
  const isSave = (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's';
  const isNewNote =
    (event.ctrlKey || event.metaKey) && event.shiftKey && event.key.toLowerCase() === 'n';

  if (isSave) {
    event.preventDefault();
    saveNote();
  }

  if (isNewNote) {
    event.preventDefault();
    resetEditor();
    titleInput.focus();
    showToast('已创建空白笔记', 'info');
  }
}

async function safeParse(res) {
  try {
    return await res.json();
  } catch (e) {
    return {};
  }
}

bootstrap();
