import { useRef, useState } from 'react'
import {
  Apple,
  ArrowRight,
  Camera,
  ChefHat,
  CircleHelp,
  Clock3,
  Leaf,
  LoaderCircle,
  MessageCircle,
  Salad,
  ShieldCheck,
  Sparkles,
  Upload,
  Utensils,
  WandSparkles
} from 'lucide-react'

// Correct Render backend URL
const API = 'https://foodverseai-backend.onrender.com/api'

export default function App() {
  const [tab, setTab] = useState('analyze')
  const [image, setImage] = useState('')
  const [imageName, setImageName] = useState('')
  const [analysis, setAnalysis] = useState('')
  const [mode, setMode] = useState('')
  const [busy, setBusy] = useState(false)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [error, setError] = useState('')

  const fileRef = useRef(null)

  function chooseImage(file) {
    setError('')
    setAnalysis('')
    setAnswer('')

    if (!file) return

    if (!file.type.startsWith('image/')) {
      setError('Please choose a food image in JPG, PNG, or WEBP format.')
      return
    }

    if (file.size > 8 * 1024 * 1024) {
      setError('Image size must be less than 8 MB.')
      return
    }

    const reader = new FileReader()

    reader.onload = () => {
      setImage(reader.result)
      setImageName(file.name)
    }

    reader.onerror = () => {
      setError('Could not read the selected image. Please try again.')
    }

    reader.readAsDataURL(file)
  }

  async function sendRequest(endpoint, payload) {
    let response

    try {
      response = await fetch(`${API}/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })
    } catch {
      throw new Error(
        'Could not connect to the backend. Please check the backend URL and try again.'
      )
    }

    let data

    try {
      data = await response.json()
    } catch {
      throw new Error(
        `The backend returned an invalid response (HTTP ${response.status}).`
      )
    }

    if (!response.ok) {
      throw new Error(
        data.error ||
        data.message ||
        `Request failed with HTTP ${response.status}.`
      )
    }

    return data
  }

  async function analyzeImage() {
    if (!image) {
      setError('First, upload a food image.')
      return
    }

    setBusy(true)
    setError('')
    setAnalysis('')
    setAnswer('')
    setMode('')

    try {
      const data = await sendRequest('analyze-food', { image })

      setAnalysis(
        data.result ||
        data.analysis ||
        'The backend did not return an analysis result.'
      )

      setMode(data.mode || 'AI')
    } catch (err) {
      setError(
        err.message || 'Food analysis failed. Please try again.'
      )
    } finally {
      setBusy(false)
    }
  }

  async function askAssistant(e) {
    e.preventDefault()

    if (!question.trim()) {
      setError('Please enter a question first.')
      return
    }

    setBusy(true)
    setError('')
    setAnswer('')
    setAnalysis('')
    setMode('')

    try {
      const data = await sendRequest('assistant', {
        question: question.trim()
      })

      setAnswer(
        data.result ||
        data.answer ||
        'The assistant did not return an answer.'
      )

      setMode(data.mode || 'AI')
    } catch (err) {
      setError(
        err.message || 'Could not get an answer. Please try again.'
      )
    } finally {
      setBusy(false)
    }
  }

  const features = [
    {
      icon: Camera,
      title: 'Food recognition',
      text: 'Upload a photo to explore what may be on your plate.'
    },
    {
      icon: Salad,
      title: 'Nutrition insights',
      text: 'Get approximate nutrition guidance for your food.'
    },
    {
      icon: ShieldCheck,
      title: 'Freshness observations',
      text: 'Review visible signs with clear safety limitations.'
    },
    {
      icon: ChefHat,
      title: 'Cooking assistant',
      text: 'Turn ingredients and questions into cooking ideas.'
    }
  ]

  return (
    <div className="app-shell">
      <header className="topbar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault()
            setTab('analyze')
            setError('')
          }}
          aria-label="Food Verse AI home"
        >
          <span className="brand-icon">
            <Apple size={23} />
          </span>

          <span>
            foodverse<span className="brand-ai">.ai</span>
            <small>FOOD, UNDERSTOOD.</small>
          </span>
        </a>

        <nav>
          <button
            className={tab === 'analyze' ? 'nav-link active' : 'nav-link'}
            onClick={() => {
              setTab('analyze')
              setError('')
            }}
          >
            Food analyzer
          </button>

          <button
            className={tab === 'assistant' ? 'nav-link active' : 'nav-link'}
            onClick={() => {
              setTab('assistant')
              setError('')
            }}
          >
            AI assistant
          </button>

          <a
            className="github-link"
            href="https://github.com/devadeva1604/FoodVerseAI"
            target="_blank"
            rel="noreferrer"
          >
            GitHub <ArrowRight size={15} />
          </a>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow">
              <Sparkles size={15} />
              YOUR PERSONAL FOOD INTELLIGENCE
            </div>

            <h1>
              A little more insight.
              <br />
              <em>A lot more</em> <span>nourishment.</span>
            </h1>

            <p>
              Explore the food you eat, discover cooking ideas, and make
              more informed choices — all in one friendly place.
            </p>

            <div className="hero-points">
              <span>
                <Leaf size={16} /> Thoughtful insights
              </span>
              <span>
                <Clock3 size={16} /> Simple to use
              </span>
            </div>
          </div>

          <div
            className="hero-art"
            aria-label="Illustration of a healthy bowl"
          >
            <div className="sun-disc"></div>
            <div className="art-leaf leaf-one">✦</div>

            <div className="food-bowl">
              <div className="bowl-inner">
                <span className="food tomato"></span>
                <span className="food avocado"></span>
                <span className="food carrot"></span>
                <span className="food greens"></span>
                <span className="food grain"></span>
                <span className="food egg"></span>
              </div>
            </div>

            <div className="floating-card">
              <span className="float-check">✓</span>
              <span>
                <b>Good choices start here</b>
                <small>Curiosity meets nutrition</small>
              </span>
            </div>
          </div>
        </section>

        <section className="feature-grid">
          {features.map(({ icon: Icon, title, text }) => (
            <article className="feature-card" key={title}>
              <span className="feature-icon">
                <Icon size={20} />
              </span>
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </section>

        <section className="workspace">
          <div className="section-heading">
            <div>
              <div className="eyebrow">LET'S GET STARTED</div>
              <h2>What’s on your mind?</h2>
            </div>

            <span className="beta-pill">
              <span></span> AI workspace
            </span>
          </div>

          <div className="tabs">
            <button
              className={tab === 'analyze' ? 'tab active' : 'tab'}
              onClick={() => {
                setTab('analyze')
                setError('')
              }}
            >
              <Camera size={17} /> Analyze food
            </button>

            <button
              className={tab === 'assistant' ? 'tab active' : 'tab'}
              onClick={() => {
                setTab('assistant')
                setError('')
              }}
            >
              <MessageCircle size={17} /> Ask the assistant
            </button>
          </div>

          {tab === 'analyze' ? (
            <div className="analyzer-layout">
              <div className="upload-panel">
                <div className="panel-title">
                  <span className="step-number">01</span>
                  <div>
                    <h3>Upload a food photo</h3>
                    <p>A clear, well-lit photo works best.</p>
                  </div>
                </div>

                <input
                  ref={fileRef}
                  className="hidden-input"
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  onChange={(e) => chooseImage(e.target.files?.[0])}
                />

                <button
                  type="button"
                  className={image ? 'dropzone has-image' : 'dropzone'}
                  onClick={() => fileRef.current?.click()}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault()
                    chooseImage(e.dataTransfer.files?.[0])
                  }}
                >
                  {image ? (
                    <>
                      <img src={image} alt="Uploaded food preview" />
                      <span className="file-label">{imageName}</span>
                      <span className="change-photo">
                        Choose another photo
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="upload-icon">
                        <Upload size={24} />
                      </span>
                      <b>Drop your image here</b>
                      <span>or click to browse files</span>
                      <small>PNG, JPG or WEBP · Max 8 MB</small>
                    </>
                  )}
                </button>

                <button
                  type="button"
                  className="primary-button"
                  onClick={analyzeImage}
                  disabled={busy}
                >
                  {busy ? (
                    <>
                      <LoaderCircle className="spin" size={18} />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <WandSparkles size={18} />
                      Analyze my food
                      <ArrowRight size={17} />
                    </>
                  )}
                </button>

                <p className="privacy-note">
                  <ShieldCheck size={14} />
                  Your image is sent to the backend for analysis.
                </p>
              </div>

              <div className="result-panel">
                <div className="panel-title">
                  <span className="step-number">02</span>
                  <div>
                    <h3>Your food insights</h3>
                    <p>Results appear here after analysis.</p>
                  </div>
                </div>

                {analysis ? (
                  <div className="result-content">
                    <span className="result-badge">
                      <Sparkles size={14} />
                      {mode === 'AI' ? 'AI ANALYSIS' : 'DEMO MODE'}
                    </span>
                    <p className="result-text">{analysis}</p>
                  </div>
                ) : (
                  <div className="empty-result">
                    <div className="empty-illustration">
                      <Utensils size={29} />
                      <Sparkles size={17} />
                    </div>
                    <h4>Your insights are cooking</h4>
                    <p>
                      Upload a photo and select “Analyze my food” to get
                      started.
                    </p>
                    <div className="result-skeleton">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="assistant-panel">
              <div className="assistant-intro">
                <span className="assistant-avatar">
                  <ChefHat size={25} />
                </span>
                <div>
                  <h3>Your friendly food assistant</h3>
                  <p>
                    Ask for recipes, ingredient swaps, or everyday
                    nutrition ideas.
                  </p>
                </div>
              </div>

              <form onSubmit={askAssistant}>
                <label htmlFor="question">
                  What would you like help with?
                </label>

                <textarea
                  id="question"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="e.g. I have tomatoes, rice and eggs. What can I cook?"
                  rows="4"
                />

                <button
                  type="submit"
                  className="primary-button"
                  disabled={busy || !question.trim()}
                >
                  {busy ? (
                    <>
                      <LoaderCircle className="spin" size={18} />
                      Thinking...
                    </>
                  ) : (
                    <>
                      Ask Food Verse AI
                      <ArrowRight size={17} />
                    </>
                  )}
                </button>
              </form>

              {answer && (
                <div className="assistant-answer">
                  <span className="result-badge">
                    <Sparkles size={14} />
                    {mode === 'AI' ? 'AI ANSWER' : 'DEMO MODE'}
                  </span>
                  <p className="result-text">{answer}</p>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="error-message" role="alert">
              <CircleHelp size={17} />
              {error}
            </div>
          )}

          <div className="safety-note">
            <ShieldCheck size={18} />
            <p>
              <b>A thoughtful note on food safety</b>
              <br />
              Image-based analysis can be uncertain. It cannot confirm
              that food is safe to eat or replace professional dietary advice.
            </p>
          </div>
        </section>

        <section className="bottom-cta">
          <div className="cta-icon">
            <Salad size={26} />
          </div>

          <div>
            <h2>Better food choices, one step at a time.</h2>
            <p>Start with a question. Leave with a little more knowledge.</p>
          </div>

          <button
            type="button"
            onClick={() => {
              setTab('assistant')
              window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
              })
            }}
          >
            Ask a question <ArrowRight size={16} />
          </button>
        </section>
      </main>

      <footer>
        <a className="footer-brand" href="#">
          foodverse.ai
        </a>
        <span>Built with curiosity and care.</span>
        <span>Food Verse AI · Capstone Project</span>
      </footer>
    </div>
  )
}