import shield from '@/assets/shield.png'
import { cn } from '@/lib/utils'

/**
 * Aegix mark — the striped-shield crest. The source art is near-black ink on
 * transparency, so dark mode inverts it to white; it stays legible on both
 * themes without shipping two assets.
 */
export function LogoMark({ className }: { className?: string }) {
  return (
    <img
      src={shield}
      alt=''
      aria-hidden='true'
      className={cn('shrink-0 object-contain dark:invert', className)}
    />
  )
}

export function Wordmark({ className }: { className?: string }) {
  return (
    <div className={cn('flex items-center gap-2.5', className)}>
      <LogoMark className='size-8' />
      <div className='leading-none'>
        <p className='text-[15px] font-semibold tracking-tight'>
          Aegix <span className='text-primary'>AI</span>
        </p>
        <p className='text-muted-foreground mt-1 text-[11px]'>
          Every clause, checked against the law
        </p>
      </div>
    </div>
  )
}
