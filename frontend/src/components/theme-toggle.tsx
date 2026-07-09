import { Moon, Sun } from '@phosphor-icons/react'
import { useTheme } from '@/lib/theme'
import { cn } from '@/lib/utils'

export function ThemeToggle({ className }: { className?: string }) {
  const { theme, toggle } = useTheme()
  return (
    <button
      onClick={toggle}
      aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
      className={cn(
        'text-muted-foreground hover:bg-secondary hover:text-foreground flex size-8 items-center justify-center rounded-lg transition-colors',
        className
      )}
    >
      {theme === 'dark' ? (
        <Sun className='size-4.5' />
      ) : (
        <Moon className='size-4.5' />
      )}
    </button>
  )
}
