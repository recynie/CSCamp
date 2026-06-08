export type Urgency = 'critical' | 'soon' | 'near' | 'far' | 'unknown' | 'expired';

export interface Camp {
  school: string;
  institute: string;
  title: string;
  url: string;
  deadline: string | null;  // "YYYY-MM-DD" or null
  expired: boolean;
  category: string;
  tags: string[];            // ["TOP2", "C9", "985", ...]
  urgency: Urgency;
  source: string;            // "shenyanpai" | "boardcaster"
}

export interface CampsData {
  updated_at: string;
  total: number;
  camps: Camp[];
}

export interface FilterState {
  query: string;
  urgency: Set<Urgency>;
  categories: Set<string>;
  tags: Set<string>;         // 学校档次标签筛选
  schools: Set<string>;
  showExpired: boolean;
  showUnknown: boolean;
}
