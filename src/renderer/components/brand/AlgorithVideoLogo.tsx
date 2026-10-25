import lockupUrl from '../../../../resources/algorithvideo-logo.svg'
import iconUrl from '../../../../resources/algorithvideo-icon-small.svg'
import markUrl from '../../../../resources/algorithvideo-mark.svg'
import { cn } from '../../lib/utils'

interface AlgorithVideoLogoProps {
  /**
   * lockup: Supplied AlgorithVideo mark + outlined wordmark (artwork is for dark surfaces).
   * icon:   the app icon tile, the supplied white frame and yellow play emblem.
   * mark:   the mark alone, for tight spaces such as the collapsed sidebar.
   */
  variant?: 'lockup' | 'icon' | 'mark'
  /** Size by height (e.g. "h-6"); width follows the artwork. */
  className?: string
  alt?: string
}

/**
 * AlgorithVideo brand artwork. Regenerate the exports with
 * npm run icons.
 */
export function AlgorithVideoLogo({ variant = 'lockup', className, alt = 'AlgorithVideo' }: AlgorithVideoLogoProps): React.JSX.Element {
  return (
    <img
      src={variant === 'icon' ? iconUrl : variant === 'mark' ? markUrl : lockupUrl}
      alt={alt}
      draggable={false}
      className={cn('w-auto shrink-0 select-none', className)}
    />
  )
}
