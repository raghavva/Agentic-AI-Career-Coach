import React, { useMemo, useState } from 'react';
import './App.css';

type Course = {
  title?: string;
  course_title?: string;
  platform?: string | string[];
  rating?: string | number | string[];
  duration?: string | string[];
  price?: string | string[];
  instructor?: string | string[];
  description?: string | string[];
  course_description?: string | string[];
  course_url?: string;
  url?: string;
  link?: string;
  data?: Record<string, any>;
  [k: string]: any;
};

type AnalyzeResponse = {
  career_goal: string;
  student_skills: string[];
  ideal_skills: string[];
  missing_skills: string[];
  courses_found: number;
  top_5_courses: Course[];
};

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

const pickText = (v: any): string => {
  if (!v && v !== 0) return '';
  if (Array.isArray(v)) return v.filter(Boolean).map(String).join(' • ');
  if (typeof v === 'object') return '';
  return String(v);
};

const getFromKeys = (obj: any, keys: string[]): any =>
  keys.map(k => obj?.[k]).find(v => v !== undefined && v !== null);

const getNested = (obj: any, keys: string[]): string =>
  pickText(getFromKeys(obj, keys) ?? getFromKeys(obj?.data || {}, keys));

const courseTitle = (c: Course) =>
  pickText(c.course_title) || pickText(c.title) || 'Untitled Course';

const courseDesc = (c: Course) =>
  getNested(c, ['course_description', 'description', 'course_descriptions']) || 'No description';

const coursePlatform = (c: Course) =>
  getNested(c, ['platform', 'platforms']) || 'N/A';

const courseURL = (c: Course) =>
  (c.course_url as string) || (c.url as string) || (c.link as string) || c?.data?.course_url || '';

const rating = (c: Course) => getNested(c, ['rating', 'ratings']) || 'N/A';
const duration = (c: Course) => getNested(c, ['duration', 'durations']) || 'N/A';
const price = (c: Course) => getNested(c, ['price', 'prices']) || 'N/A';
const instructor = (c: Course) => getNested(c, ['instructor', 'instructors']) || 'N/A';

function App() {
  const [careerGoal, setCareerGoal] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showConfetti, setShowConfetti] = useState(false);

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type === 'application/pdf') setResumeFile(file);
    else setError('Please drop a valid PDF file.');
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setShowConfetti(false);

    if (!careerGoal || !resumeFile) {
      setError('Please provide both a career goal and a resume PDF.');
      return;
    }

    try {
      setLoading(true);
      const form = new FormData();
      form.append('career_goal', careerGoal);
      form.append('resume', resumeFile, resumeFile.name);

      const res = await fetch(`${API_BASE}/analyze`, { method: 'POST', body: form });
      if (!res.ok) throw new Error(await res.text());
      const data: AnalyzeResponse = await res.json();
      setResult(data);

      setTimeout(() => setShowConfetti(true), 250);
      setTimeout(() => setShowConfetti(false), 3500);
    } catch (err: any) {
      setError(err?.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  const stagger = useMemo(() => (idx: number) => ({ animationDelay: `${idx * 90}ms` }), []);

  return (
    <div className="app">
      <div className="bg-gradient animated" />
      <div className="dot-grid" />

      <header className="hero pop-in">
        <div className="badge pulse">New</div>
        <h1 className="title-glow">CareerPath AI</h1>
        <p className="subtitle-fade">From resume to top 5 courses — personalized by AI.</p>
        <div className="hero-stats float">
          <div className="stat card-float">
            <div className="stat-num">10k+</div>
            <div className="stat-label">Skills Analyzed</div>
          </div>
          <div className="divider" />
          <div className="stat card-float">
            <div className="stat-num">2k+</div>
            <div className="stat-label">Courses Ranked</div>
          </div>
          <div className="divider" />
          <div className="stat card-float">
            <div className="stat-num">5</div>
            <div className="stat-label">Best Picks</div>
          </div>
        </div>
      </header>

      <main className="container">
        <form className="glass-card hover-tilt" onSubmit={onSubmit}>
          <h2 className="card-title glow-underline">Analyze & Recommend</h2>

          <label className="label">Career Goal</label>
          <div className="input-wrap">
            <input
              className="input"
              type="text"
              value={careerGoal}
              onChange={(e) => setCareerGoal(e.target.value)}
              placeholder="e.g., Senior Data Scientist"
            />
            <div className="input-accent" />
          </div>

          <label className="label">Resume (PDF)</label>
          <div
            className={`dropzone ${dragging ? 'dragging' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
          >
            <input
              id="resume-input"
              type="file"
              accept="application/pdf"
              onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
              hidden
            />
            <div className="dropzone-inner" onClick={() => document.getElementById('resume-input')?.click()}>
              <div className="drop-icon spin">📄</div>
              {resumeFile ? (
                <p className="drop-text">
                  Selected: <strong>{resumeFile.name}</strong>
                </p>
              ) : (
                <p className="drop-text">
                  Drag & drop your PDF here, or <span className="link">browse</span>
                </p>
              )}
              <p className="hint">PDF only. Max 10MB.</p>
              <div className="scan-laser" />
            </div>
          </div>

          {error && <div className="alert error slide-down">{error}</div>}

          <button className={`btn ${loading ? 'loading' : ''} hover-pop`} type="submit" disabled={loading}>
            {loading ? <span className="spinner" /> : 'Analyze & Recommend'}
          </button>

          {loading && (
            <div className="progress-track">
              <div className="progress-bar" />
            </div>
          )}
        </form>

        {loading && (
          <div className="glass-card loading-card fade-in">
            <div className="loading-title shimmer" />
            <div className="loading-grid">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="loading-line shimmer" />
              ))}
            </div>
            <div className="loading-courses">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="loading-course shimmer" />
              ))}
            </div>
          </div>
        )}

        {result && (
          <section className="results fade-in-up">
            <div className="metrics">
              <div className="metric-card lift">
                <div className="metric-label">Career Goal</div>
                <div className="metric-value">{result.career_goal}</div>
              </div>
              <div className="metric-card lift">
                <div className="metric-label">Student Skills</div>
                <div className="metric-value">{result.student_skills.length}</div>
              </div>
              <div className="metric-card lift">
                <div className="metric-label">Required Skills</div>
                <div className="metric-value">{result.ideal_skills.length}</div>
              </div>
              <div className="metric-card lift">
                <div className="metric-label">Missing Skills</div>
                <div className="metric-value">{result.missing_skills.length}</div>
              </div>
            </div>

            {!!result.missing_skills.length && (
              <div className="chip-marquee">
                <div className="chips track">
                  {result.missing_skills.concat(result.missing_skills).map((s, i) => (
                    <span key={`${s}-${i}`} className="chip">{s}</span>
                  ))}
                </div>
              </div>
            )}

            <h3 className="section-title">Top 5 Recommended Courses</h3>
            <div className="courses">
              {(result.top_5_courses || []).map((c, idx) => (
                <div key={idx} className="course-card reveal" style={stagger(idx)}>
                  <div className="course-rank glow">#{idx + 1}</div>
                  <div className="course-header">
                    <h4 className="course-title">{courseTitle(c)}</h4>
                    <span className="badge-soft">{coursePlatform(c)}</span>
                  </div>
                  <p className="course-desc">{courseDesc(c)}</p>
                  <div className="course-meta">
                    <div className="meta-item"><span>⭐</span>{rating(c)}</div>
                    <div className="meta-item"><span>⏱️</span>{duration(c)}</div>
                    <div className="meta-item"><span>💲</span>{price(c)}</div>
                    <div className="meta-item"><span>👤</span>{instructor(c)}</div>
                  </div>
                  {courseURL(c) ? (
                    <a className="link-btn hover-pop" href={courseURL(c)} target="_blank" rel="noreferrer">Open Course →</a>
                  ) : (
                    <div className="muted">No course link available</div>
                  )}
                  <div className="card-sheen" />
                </div>
              ))}
            </div>
          </section>
        )}
      </main>

      {showConfetti && <div className="confetti" aria-hidden="true" />}

      <footer className="footer fade-in">
        <span>🚀 Powered by AI • Built for Career Growth</span>
      </footer>
    </div>
  );
}

export default App;