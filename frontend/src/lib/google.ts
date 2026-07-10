/**
 * Google sign-in via Google Identity Services — no auth backend needed.
 * The app only wants a verified name/email/photo to key local history by,
 * so the ID token is decoded client-side and never sent anywhere.
 */

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID ?? ''

/** The Google button is only offered when a client ID is configured. */
export const GOOGLE_CONFIGURED = Boolean(CLIENT_ID)

export interface GoogleProfile {
  name: string
  email: string
  avatarUrl?: string
}

let scriptPromise: Promise<void> | null = null

function loadScript(): Promise<void> {
  scriptPromise ??= new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = 'https://accounts.google.com/gsi/client'
    s.async = true
    s.onload = () => resolve()
    s.onerror = () => reject(new Error('Google Sign-In failed to load'))
    document.head.appendChild(s)
  })
  return scriptPromise
}

function decodeProfile(credential: string): GoogleProfile {
  const b64 = credential.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
  const claims = JSON.parse(atob(b64)) as {
    name?: string
    email: string
    picture?: string
  }
  return {
    name: claims.name || claims.email.split('@')[0],
    email: claims.email,
    avatarUrl: claims.picture,
  }
}

/** Render Google's official sign-in button into `el`. */
export async function renderGoogleButton(
  el: HTMLElement,
  theme: 'light' | 'dark',
  onProfile: (profile: GoogleProfile) => void
): Promise<void> {
  await loadScript()
  const google = (
    window as unknown as {
      google: {
        accounts: {
          id: {
            initialize: (config: object) => void
            renderButton: (el: HTMLElement, options: object) => void
          }
        }
      }
    }
  ).google
  google.accounts.id.initialize({
    client_id: CLIENT_ID,
    callback: (response: { credential: string }) =>
      onProfile(decodeProfile(response.credential)),
  })
  google.accounts.id.renderButton(el, {
    theme: theme === 'dark' ? 'filled_black' : 'outline',
    size: 'large',
    shape: 'pill',
    text: 'continue_with',
    width: 320,
  })
}
