import type { ReactNode } from 'react';

interface Props {
  sidebar: ReactNode;
  children: ReactNode;
}

export default function Layout({ sidebar, children }: Props) {
  return (
    <div className="layout">
      <div className="sidebar-panel">
        {sidebar}
      </div>
      <div className="main-panel">
        {children}
      </div>
    </div>
  );
}
