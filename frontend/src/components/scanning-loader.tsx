import { useEffect, useState } from 'react'
import {
  CheckCircle,
  CircleNotch,
  Prohibit,
  Question,
  Warning,
} from '@phosphor-icons/react'
import type { Progress } from '@/app'
import type { Verdict } from '@/lib/api'
import { categoryLabel } from '@/lib/labels'
import { cn } from '@/lib/utils'

const VERDICT_META: Record<
  Verdict,
  { icon: typeof CheckCircle; dot: string; text: string }
> = {
  Compliant: {
    icon: CheckCircle,
    dot: 'bg-emerald-500',
    text: 'text-emerald-600 dark:text-emerald-400',
  },
  'Non-compliant': {
    icon: Warning,
    dot: 'bg-red-500',
    text: 'text-red-600 dark:text-red-400',
  },
  Vague: {
    icon: Question,
    dot: 'bg-amber-500',
    text: 'text-amber-600 dark:text-amber-400',
  },
  Missing: {
    icon: Prohibit,
    dot: 'bg-zinc-400',
    text: 'text-zinc-600 dark:text-zinc-300',
  },
}

const SEGMENTING_MESSAGES = [
  'Reading the contract…',
  'Extracting the text layer…',
  'Finding clause boundaries…',
  'Identifying what each clause covers…',
]

const RETRIEVAL_MESSAGES = [
  'Retrieving the governing provisions…',
  'Searching the Labor Code…',
  'Matching clauses to statutes…',
]

/** Cycle a list of strings on an interval, restarting when the list changes. */
function useTicker(period = 1900) {
  const [tick, setTick] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), period)
    return () => clearInterval(id)
  }, [period])
  return tick
}

export function ScanningLoader({ progress }: { progress: Progress }) {
  const { stage, total, clauses, verdicts } = progress
  const done = Object.keys(verdicts).length
  const pct = total ? Math.round((done / total) * 100) : 0
  const tick = useTicker()

  // While judging, name the clauses that are actually still outstanding —
  // the status line reports real work, not a canned script.
  const pending = clauses.filter((c) => verdicts[c.index] === undefined)
  let messages: string[]
  if (stage === 'segmenting') {
    messages = SEGMENTING_MESSAGES
  } else if (pending.length > 0) {
    messages = [
      ...pending.map((c) => `Checking ${categoryLabel(c.clause_type)}…`),
      ...RETRIEVAL_MESSAGES,
    ]
  } else {
    messages = ['Compiling your compliance report…']
  }
  const message = messages[tick % messages.length]

  return (
    <div className='flex w-full flex-1 flex-col items-center justify-center py-8'>
      <div className='relative w-full max-w-lg'>
        <div className='bg-primary/10 absolute -inset-4 rounded-3xl blur-2xl' />

        <div className='border-border/70 bg-card relative overflow-hidden rounded-xl border shadow-xl'>
          {/* Header + progress bar */}
          <div className='border-border/60 border-b px-4 py-3'>
            <div className='flex items-center justify-between gap-3'>
              <p className='text-sm font-medium'>
                {stage === 'segmenting'
                  ? 'Reading the contract'
                  : 'Checking clauses against the Labor Code'}
              </p>
              {total > 0 && (
                <span className='text-muted-foreground shrink-0 text-xs tabular-nums'>
                  {done}/{total}
                </span>
              )}
            </div>
            <div className='bg-secondary mt-2.5 h-1 overflow-hidden rounded-full'>
              <div
                className={cn(
                  'bg-primary h-full rounded-full transition-all duration-500',
                  total === 0 && 'w-1/3 animate-pulse'
                )}
                style={total ? { width: `${pct}%` } : undefined}
              />
            </div>
          </div>

          <div className='relative'>
            {/* Segmenting: no clauses known yet, show placeholder lines */}
            {total === 0 && (
              <div className='space-y-3 px-4 py-5'>
                {['82%', '95%', '68%', '90%', '74%'].map((w, i) => (
                  <div
                    key={i}
                    className='bg-muted-foreground/20 h-2.5 rounded-full'
                    style={{ width: w }}
                  />
                ))}
              </div>
            )}

            {/* Judging: one row per real clause, resolving as verdicts land */}
            {total > 0 && (
              <ul className='divide-border/50 divide-y'>
                {clauses.map(({ index, clause_type }) => {
                  const verdict = verdicts[index]
                  const meta = verdict ? VERDICT_META[verdict] : null
                  const Icon = meta?.icon
                  return (
                    <li
                      key={index}
                      className={cn(
                        'flex items-center gap-3 px-4 py-2.5 transition-colors',
                        verdict ? 'bg-transparent' : 'bg-muted/20'
                      )}
                    >
                      <span
                        className={cn(
                          'size-1.5 shrink-0 rounded-full',
                          meta ? meta.dot : 'bg-muted-foreground/30'
                        )}
                      />
                      <span
                        className={cn(
                          'flex-1 truncate text-sm',
                          verdict ? 'font-medium' : 'text-muted-foreground'
                        )}
                      >
                        {categoryLabel(clause_type)}
                      </span>
                      {verdict && Icon && meta ? (
                        <span
                          className={cn(
                            'flag-pop flex shrink-0 items-center gap-1 text-xs font-medium',
                            meta.text
                          )}
                        >
                          <Icon className='size-3.5' />
                          {verdict}
                        </span>
                      ) : (
                        <CircleNotch className='text-muted-foreground size-3.5 shrink-0 animate-spin' />
                      )}
                    </li>
                  )
                })}
              </ul>
            )}

            {/* Scan beam only while work is outstanding */}
            {done < total || total === 0 ? (
              <div className='scan-beam pointer-events-none absolute inset-x-0 top-0'>
                <div className='via-primary/70 h-0.5 bg-gradient-to-r from-transparent to-transparent' />
                <div className='from-primary/20 h-12 bg-gradient-to-b to-transparent' />
              </div>
            ) : null}
          </div>
        </div>
      </div>

      {/* Rotating status — the message names work actually outstanding */}
      <p
        key={message}
        aria-live='polite'
        className='text-muted-foreground flag-pop mt-6 min-h-5 text-center text-sm'
      >
        {message}
      </p>
      {total > 0 && (
        <p className='text-muted-foreground/70 mt-1.5 text-center text-xs'>
          {done} of {total} clauses checked — results appear as each finishes.
        </p>
      )}
    </div>
  )
}
