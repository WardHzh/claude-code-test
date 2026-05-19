export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface SSEEvent {
  type: 'token' | 'tool_start' | 'tool_end' | 'done' | 'error';
  content?: string;
  tool?: string;
  input?: string;
}
