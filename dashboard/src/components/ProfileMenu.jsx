import React, { useState, useRef, useEffect } from 'react';
import { User, CreditCard, LogOut, Sparkles } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

// Header avatar + dropdown for signed-in cloud users: shows the email and gives
// access to Account & billing (manage subscription, top-ups) and Sign out.
export default function ProfileMenu() {
  const { user, isManaged, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    if (!open) return;
    const onClick = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, [open]);

  if (!user) return null;
  const initial = (user.email || '?').trim().charAt(0).toUpperCase();

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label="Account menu"
        className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 text-primary flex items-center justify-center text-sm font-semibold hover:bg-primary/30 transition-colors"
      >
        {initial}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-60 z-30 bg-surface border border-white/10 rounded-xl shadow-xl overflow-hidden animate-[fadeIn_0.15s_ease-out]">
          <div className="px-4 py-3 border-b border-white/5">
            <p className="text-xs text-zinc-500">Signed in as</p>
            <p className="text-sm text-white truncate" title={user.email}>{user.email}</p>
          </div>
          {!isManaged && (
            <button
              onClick={() => { setOpen(false); window.location.hash = '#/pricing'; }}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-primary hover:bg-white/5 transition-colors"
            >
              <Sparkles size={16} /> Start free trial
            </button>
          )}
          <button
            onClick={() => { setOpen(false); window.location.hash = '#/account'; }}
            className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-zinc-200 hover:bg-white/5 transition-colors"
          >
            <CreditCard size={16} /> Account &amp; billing
          </button>
          <button
            onClick={() => { setOpen(false); logout(); }}
            className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-zinc-200 hover:bg-white/5 transition-colors border-t border-white/5"
          >
            <LogOut size={16} /> Sign out
          </button>
        </div>
      )}
    </div>
  );
}
