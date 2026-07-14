import React, { useState, useEffect } from 'react';
import { Loader2, Download, History as HistoryIcon, Film } from 'lucide-react';
import { apiJson } from '../lib/api';

// The signed-in user's saved video library (stored in R2). Private, signed links.
export default function HistoryTab() {
  const [videos, setVideos] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    apiJson('/api/history')
      .then((d) => setVideos(d.videos || []))
      .catch(() => setError('Could not load your library.'));
  }, []);

  const fmtDate = (iso) => (iso ? new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) : '');

  if (videos === null && !error) {
    return <div className="flex justify-center py-20"><Loader2 className="animate-spin text-primary" /></div>;
  }

  return (
    <div className="h-full overflow-y-auto p-8 max-w-5xl mx-auto animate-[fadeIn_0.3s_ease-out]">
      <div className="flex items-center gap-3 mb-2">
        <HistoryIcon className="text-primary" />
        <h1 className="text-2xl font-bold">Your library</h1>
      </div>
      <p className="text-zinc-400 text-sm mb-8">
        All the shorts you've generated, saved while your plan is active. Kept for 7 days after your plan ends.
      </p>

      {error && <p className="text-red-400 text-sm">{error}</p>}

      {videos && videos.length === 0 && (
        <div className="text-center py-20 text-zinc-500">
          <Film size={40} className="mx-auto mb-4 opacity-50" />
          <p>No videos yet. Generate your first short from the Clip Generator.</p>
        </div>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
        {(videos || []).map((v) => (
          <div key={v.id} className="bg-surface border border-white/10 rounded-xl overflow-hidden group">
            <div className="aspect-[9/16] bg-black">
              <video src={v.view_url} controls preload="metadata" className="w-full h-full object-contain" />
            </div>
            <div className="p-3">
              <p className="text-sm font-medium line-clamp-2 mb-1" title={v.title}>{v.title || 'Short'}</p>
              <div className="flex items-center justify-between">
                <span className="text-[11px] text-zinc-500">{fmtDate(v.created_at)}</span>
                <a href={v.download_url} className="text-primary hover:text-blue-400 flex items-center gap-1 text-xs" title="Download">
                  <Download size={14} /> Download
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
