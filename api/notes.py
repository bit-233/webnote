from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

import storage
from .security import require_auth


class NoteCreate(BaseModel):
    title: str = Field("", description="笔记标题")
    content: str = Field("", description="笔记内容")
    tags: Optional[List[str]] = Field(default_factory=list)


class Note(NoteCreate):
    id: str
    created_at: str
    updated_at: str


router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.get("", response_model=List[Note])
def list_all_notes(query: str = "", tag: str = ""):
    return storage.list_notes(query=query, tag=tag)


@router.get("/{note_id}", response_model=Note)
def get_single_note(note_id: str):
    note = storage.get_note(note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="笔记不存在")
    return note


@router.post("", response_model=Note, dependencies=[Depends(require_auth)])
def create_note(payload: NoteCreate):
    return storage.create_note(payload.title, payload.content, payload.tags)


@router.put("/{note_id}", response_model=Note, dependencies=[Depends(require_auth)])
def update_note(note_id: str, payload: NoteCreate):
    note = storage.update_note(note_id, payload.title, payload.content, payload.tags)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="笔记不存在")
    return note


@router.delete("/{note_id}", dependencies=[Depends(require_auth)])
def delete_note(note_id: str):
    if not storage.delete_note(note_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="笔记不存在")
    return {"ok": True}
